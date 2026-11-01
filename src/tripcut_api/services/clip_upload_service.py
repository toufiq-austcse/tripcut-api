from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from psycopg import Connection

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.config.limits_constants import (
    ALLOWED_CONTENT_TYPE_PREFIX,
    MAX_CLIPS_PER_TRIP,
    MAX_TRIP_BYTES,
)
from tripcut_api.config.upload_constants import ORIGINALS_PREFIX, PART_SIZE_BYTES, PRESIGNED_URL_TTL_SECONDS
from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.api_error import ApiError
from tripcut_api.repositories.clip_repository import ClipRepository
from tripcut_api.repositories.trip_repository import TripRepository
from tripcut_api.schemas.clips.create_clip_request import CreateClipRequest
from tripcut_api.services.create_clip_result import CreateClipResult
from tripcut_api.storage.r2_multipart_service import R2MultipartService


class ClipUploadService:
    """Clip lifecycle: register (starts the R2 upload), sign parts, list parts, complete, abort."""

    def __init__(
        self, conn: Connection, trips: TripRepository, clips: ClipRepository, storage: R2MultipartService
    ) -> None:
        self._conn = conn
        self._trips = trips
        self._clips = clips
        self._storage = storage

    def create_clip(self, user: CurrentUser, trip_id: UUID, body: CreateClipRequest) -> CreateClipResult:
        if not body.content_type.lower().startswith(ALLOWED_CONTENT_TYPE_PREFIX):
            raise ApiError(415, codes.UNSUPPORTED_MEDIA_TYPE, "Only video/* files can be uploaded")

        with self._conn.transaction():
            trip = self._trips.lock_owned(trip_id, user.id)
            if trip is None:
                raise ApiError(404, codes.NOT_FOUND, "Trip not found")
            if trip["status"] != "open":
                raise ApiError(409, codes.TRIP_NOT_OPEN, "The trip is not open for uploads")

            existing = self._clips.get_by_fingerprint(trip_id, body.fingerprint)
            if existing is not None:
                if existing["size_bytes"] != body.size_bytes:
                    raise ApiError(
                        422, codes.VALIDATION_ERROR, "fingerprint: already used in this trip with a different size"
                    )
                return CreateClipResult(clip=existing, created=False)

            stats = self._clips.stats_for_trip(trip_id)
            if stats["clip_count"] >= MAX_CLIPS_PER_TRIP:
                raise ApiError(413, codes.CLIP_LIMIT, f"A trip holds at most {MAX_CLIPS_PER_TRIP} clips")
            if stats["total_bytes"] + body.size_bytes > MAX_TRIP_BYTES:
                raise ApiError(413, codes.TRIP_SIZE_LIMIT, f"A trip holds at most {MAX_TRIP_BYTES} bytes")

            clip_id = uuid4()
            r2_key = f"{ORIGINALS_PREFIX}/{user.id}/{trip_id}/{clip_id}"
            part_count = (body.size_bytes + PART_SIZE_BYTES - 1) // PART_SIZE_BYTES
            upload_id = self._storage.create(r2_key, body.content_type)
            self._clips.insert(
                clip_id=clip_id,
                trip_id=trip_id,
                user_id=user.id,
                filename=body.filename,
                content_type=body.content_type,
                size_bytes=body.size_bytes,
                fingerprint=body.fingerprint,
                r2_key=r2_key,
                r2_upload_id=upload_id,
                part_size_bytes=PART_SIZE_BYTES,
                part_count=part_count,
            )
            clip = self._clips.get_owned(clip_id, user.id)
        return CreateClipResult(clip=clip, created=True)

    def sign_parts(self, user: CurrentUser, clip_id: UUID, part_numbers: list[int]) -> list[dict]:
        clip = self._require_clip(self._clips.get_owned(clip_id, user.id))
        self._require_uploading(clip)
        for part_number in part_numbers:
            if part_number < 1 or part_number > clip["part_count"]:
                raise ApiError(
                    422, codes.VALIDATION_ERROR, f"part_numbers: {part_number} is outside 1..{clip['part_count']}"
                )

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=PRESIGNED_URL_TTL_SECONDS)
        signed = []
        for part_number in sorted(set(part_numbers)):
            url = self._storage.sign_part(clip["r2_key"], clip["r2_upload_id"], part_number, PRESIGNED_URL_TTL_SECONDS)
            signed.append({"part_number": part_number, "url": url, "expires_at": expires_at})
        return signed

    def list_parts(self, user: CurrentUser, clip_id: UUID) -> dict:
        """Parts already in R2, so a client can resume after a reload. An uploaded clip lists every part."""
        clip = self._require_clip(self._clips.get_owned(clip_id, user.id))
        if clip["status"] == "uploaded":
            parts = []
            for part_number in range(1, clip["part_count"] + 1):
                size_bytes = clip["part_size_bytes"]
                if part_number == clip["part_count"]:
                    size_bytes = clip["size_bytes"] - clip["part_size_bytes"] * (clip["part_count"] - 1)
                parts.append({"part_number": part_number, "size_bytes": size_bytes})
        else:
            parts = self._storage.list_parts(clip["r2_key"], clip["r2_upload_id"])
        uploaded_bytes = sum(part["size_bytes"] for part in parts)
        return {"parts": parts, "uploaded_bytes": uploaded_bytes}

    def complete(self, user: CurrentUser, clip_id: UUID) -> dict:
        """Finish the upload from the server's own ListParts; the client sends no ETags."""
        with self._conn.transaction():
            clip = self._require_clip(self._clips.lock_owned(clip_id, user.id))
            self._require_uploading(clip)

            # Recovery: R2 finished the object on an earlier call but the row was not updated.
            finished_size = self._storage.head_size(clip["r2_key"])
            if finished_size is not None and finished_size == clip["size_bytes"]:
                self._clips.mark_uploaded(clip_id)
                return self._clips.get_owned(clip_id, user.id)

            parts = self._storage.list_parts(clip["r2_key"], clip["r2_upload_id"])
            expected_numbers = list(range(1, clip["part_count"] + 1))
            actual_numbers = [part["part_number"] for part in parts]
            uploaded_bytes = sum(part["size_bytes"] for part in parts)
            if actual_numbers != expected_numbers or uploaded_bytes != clip["size_bytes"]:
                raise ApiError(
                    409,
                    codes.PARTS_INCOMPLETE,
                    f"R2 has {len(parts)} of {clip['part_count']} parts and {uploaded_bytes} of "
                    f"{clip['size_bytes']} bytes",
                )

            self._storage.complete(clip["r2_key"], clip["r2_upload_id"], parts)
            stored_size = self._storage.head_size(clip["r2_key"])
            if stored_size != clip["size_bytes"]:
                raise ApiError(502, codes.STORAGE_ERROR, "Stored object size does not match the clip size")

            self._clips.mark_uploaded(clip_id)
            return self._clips.get_owned(clip_id, user.id)

    def abort(self, user: CurrentUser, clip_id: UUID) -> None:
        """Remove one clip: abort its R2 upload (or delete the finished object) and delete the row."""
        with self._conn.transaction():
            clip = self._require_clip(self._clips.lock_owned(clip_id, user.id))
            if clip["trip_status"] != "open":
                raise ApiError(409, codes.TRIP_NOT_OPEN, "The trip is not open for changes")
            if clip["status"] == "uploading":
                self._storage.abort(clip["r2_key"], clip["r2_upload_id"])
            else:
                self._storage.delete_object(clip["r2_key"])
            self._clips.delete(clip_id)

    def _require_clip(self, clip: dict | None) -> dict:
        if clip is None:
            raise ApiError(404, codes.NOT_FOUND, "Clip not found")
        return clip

    def _require_uploading(self, clip: dict) -> None:
        if clip["trip_status"] != "open":
            raise ApiError(409, codes.TRIP_NOT_OPEN, "The trip is not open for uploads")
        if clip["status"] != "uploading":
            raise ApiError(409, codes.CLIP_NOT_UPLOADING, "The clip is already uploaded")
