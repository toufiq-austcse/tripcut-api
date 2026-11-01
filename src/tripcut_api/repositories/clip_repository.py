from uuid import UUID

from psycopg import Connection

from tripcut_api.repositories.clip_select_sql_constants import CLIP_SELECT_SQL


class ClipRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def get_owned(self, clip_id: UUID, user_id: UUID) -> dict | None:
        return self._conn.execute(CLIP_SELECT_SQL + " where c.id = %s and c.user_id = %s", (clip_id, user_id)).fetchone()

    def lock_owned(self, clip_id: UUID, user_id: UUID) -> dict | None:
        """Lock the clip row and its trip row for the rest of the transaction."""
        return self._conn.execute(
            CLIP_SELECT_SQL + " where c.id = %s and c.user_id = %s for update of c, t", (clip_id, user_id)
        ).fetchone()

    def get_by_fingerprint(self, trip_id: UUID, fingerprint: str) -> dict | None:
        return self._conn.execute(
            CLIP_SELECT_SQL + " where c.trip_id = %s and c.fingerprint = %s", (trip_id, fingerprint)
        ).fetchone()

    def list_for_trip(self, trip_id: UUID) -> list[dict]:
        return self._conn.execute(
            CLIP_SELECT_SQL + " where c.trip_id = %s order by c.created_at, c.id", (trip_id,)
        ).fetchall()

    def stats_for_trip(self, trip_id: UUID) -> dict:
        """{clip_count, total_bytes, uploading_count} for one trip."""
        return self._conn.execute(
            "select count(*)::int as clip_count,"
            " coalesce(sum(size_bytes), 0)::bigint as total_bytes,"
            " (count(*) filter (where status = 'uploading'))::int as uploading_count"
            " from public.clips where trip_id = %s",
            (trip_id,),
        ).fetchone()

    def insert(
        self,
        clip_id: UUID,
        trip_id: UUID,
        user_id: UUID,
        filename: str,
        content_type: str,
        size_bytes: int,
        fingerprint: str,
        r2_key: str,
        r2_upload_id: str,
        part_size_bytes: int,
        part_count: int,
    ) -> None:
        self._conn.execute(
            "insert into public.clips (id, trip_id, user_id, filename, content_type, size_bytes, fingerprint,"
            " r2_key, r2_upload_id, part_size_bytes, part_count)"
            " values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                clip_id,
                trip_id,
                user_id,
                filename,
                content_type,
                size_bytes,
                fingerprint,
                r2_key,
                r2_upload_id,
                part_size_bytes,
                part_count,
            ),
        )

    def mark_uploaded(self, clip_id: UUID) -> None:
        self._conn.execute(
            "update public.clips set status = 'uploaded', uploaded_at = now(), r2_upload_id = null where id = %s",
            (clip_id,),
        )

    def delete(self, clip_id: UUID) -> None:
        self._conn.execute("delete from public.clips where id = %s", (clip_id,))
