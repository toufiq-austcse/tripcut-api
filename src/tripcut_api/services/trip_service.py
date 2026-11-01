from uuid import UUID

from psycopg import Connection

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.config.limits_constants import ACTIVE_TRIP_STATUSES, MAX_OPEN_TRIPS, MIN_CLIPS_PER_TRIP
from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.api_error import ApiError
from tripcut_api.pagination.decode_cursor import decode_cursor
from tripcut_api.pagination.encode_cursor import encode_cursor
from tripcut_api.repositories.clip_repository import ClipRepository
from tripcut_api.repositories.job_repository import JobRepository
from tripcut_api.repositories.trip_repository import TripRepository
from tripcut_api.repositories.user_repository import UserRepository
from tripcut_api.schemas.trips.update_trip_request import UpdateTripRequest
from tripcut_api.storage.r2_multipart_service import R2MultipartService


class TripService:
    """Trip lifecycle: create, read, update, delete, submit for processing."""

    def __init__(
        self,
        conn: Connection,
        users: UserRepository,
        trips: TripRepository,
        clips: ClipRepository,
        jobs: JobRepository,
        storage: R2MultipartService,
    ) -> None:
        self._conn = conn
        self._users = users
        self._trips = trips
        self._clips = clips
        self._jobs = jobs
        self._storage = storage

    def create(self, user: CurrentUser, title: str) -> dict:
        with self._conn.transaction():
            self._users.ensure_and_lock(user.id, user.email)
            active = self._trips.count_active(user.id, ACTIVE_TRIP_STATUSES)
            if active >= MAX_OPEN_TRIPS:
                raise ApiError(
                    409, codes.OPEN_TRIP_LIMIT, f"At most {MAX_OPEN_TRIPS} trips can be open or processing"
                )
            trip_id = self._trips.insert(user.id, title)
            return self._trips.get_owned(trip_id, user.id)

    def list_page(self, user: CurrentUser, limit: int, cursor: str | None) -> dict:
        page_cursor = None
        if cursor is not None:
            page_cursor = decode_cursor(cursor)
        rows = self._trips.list_page(user.id, limit + 1, page_cursor)
        next_cursor = None
        if len(rows) > limit:
            rows = rows[:limit]
            last = rows[-1]
            next_cursor = encode_cursor(last["created_at"], last["id"])
        return {"items": rows, "next_cursor": next_cursor}

    def get_detail(self, user: CurrentUser, trip_id: UUID) -> dict:
        trip = self._require_trip(self._trips.get_owned(trip_id, user.id))
        return self._with_children(trip)

    def update(self, user: CurrentUser, trip_id: UUID, body: UpdateTripRequest) -> dict:
        with self._conn.transaction():
            locked = self._require_trip(self._trips.lock_owned(trip_id, user.id))
            current = self._trips.get_owned(locked["id"], user.id)
            if body.title is None:
                title = current["title"]
            else:
                title = body.title
            if body.notify_email is None:
                notify_email = current["notify_email"]
            else:
                notify_email = body.notify_email
            self._trips.update(trip_id, title, notify_email)
            return self._trips.get_owned(trip_id, user.id)

    def delete(self, user: CurrentUser, trip_id: UUID) -> None:
        """Abort open uploads, delete stored objects, then delete the rows (clips/jobs/reels cascade)."""
        with self._conn.transaction():
            trip = self._require_trip(self._trips.lock_owned(trip_id, user.id))
            if trip["status"] == "processing":
                raise ApiError(409, codes.TRIP_NOT_OPEN, "A trip cannot be deleted while it is processing")
            for clip in self._clips.list_for_trip(trip_id):
                if clip["status"] == "uploading":
                    self._storage.abort(clip["r2_key"], clip["r2_upload_id"])
                else:
                    self._storage.delete_object(clip["r2_key"])
            for key in self._trips.list_reel_keys(trip_id):
                self._storage.delete_object(key)
            self._trips.delete(trip_id)

    def submit(self, user: CurrentUser, trip_id: UUID) -> dict:
        """Close the trip for uploads and queue the analyze job. The pipeline spawn() is SAN-52."""
        with self._conn.transaction():
            trip = self._require_trip(self._trips.lock_owned(trip_id, user.id))
            if trip["status"] != "open":
                raise ApiError(409, codes.TRIP_NOT_OPEN, "The trip was already submitted")
            stats = self._clips.stats_for_trip(trip_id)
            if stats["uploading_count"] > 0:
                raise ApiError(
                    409, codes.CLIPS_INCOMPLETE, f"{stats['uploading_count']} clips are still uploading"
                )
            if stats["clip_count"] < MIN_CLIPS_PER_TRIP:
                raise ApiError(422, codes.TOO_FEW_CLIPS, f"A trip needs at least {MIN_CLIPS_PER_TRIP} clips")
            self._jobs.insert_queued(trip_id, user.id, "analyze")
            self._trips.mark_processing(trip_id)
            submitted = self._trips.get_owned(trip_id, user.id)
            return self._with_children(submitted)

    def _with_children(self, trip: dict) -> dict:
        detail = dict(trip)
        detail["clips"] = self._clips.list_for_trip(trip["id"])
        detail["latest_job"] = self._jobs.latest_for_trip(trip["id"])
        return detail

    def _require_trip(self, trip: dict | None) -> dict:
        if trip is None:
            raise ApiError(404, codes.NOT_FOUND, "Trip not found")
        return trip
