from uuid import UUID

from psycopg import Connection

from tripcut_api.pagination.page_cursor import PageCursor
from tripcut_api.repositories.trip_select_sql_constants import TRIP_SELECT_SQL


class TripRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def insert(self, user_id: UUID, title: str) -> UUID:
        row = self._conn.execute(
            "insert into public.trips (user_id, title) values (%s, %s) returning id", (user_id, title)
        ).fetchone()
        return row["id"]

    def get_owned(self, trip_id: UUID, user_id: UUID) -> dict | None:
        return self._conn.execute(
            TRIP_SELECT_SQL + " where t.id = %s and t.user_id = %s", (trip_id, user_id)
        ).fetchone()

    def lock_owned(self, trip_id: UUID, user_id: UUID) -> dict | None:
        """Lock the trip row for the rest of the transaction. Returns {id, status} or None."""
        return self._conn.execute(
            "select id, status::text as status from public.trips where id = %s and user_id = %s for update",
            (trip_id, user_id),
        ).fetchone()

    def count_active(self, user_id: UUID, statuses: tuple[str, ...]) -> int:
        row = self._conn.execute(
            "select count(*)::int as total from public.trips where user_id = %s and status::text = any(%s)",
            (user_id, list(statuses)),
        ).fetchone()
        return row["total"]

    def list_page(self, user_id: UUID, limit: int, cursor: PageCursor | None) -> list[dict]:
        """Newest first. Returns up to `limit` rows after the cursor."""
        if cursor is None:
            return self._conn.execute(
                TRIP_SELECT_SQL + " where t.user_id = %s order by t.created_at desc, t.id desc limit %s",
                (user_id, limit),
            ).fetchall()
        return self._conn.execute(
            TRIP_SELECT_SQL
            + " where t.user_id = %s and (t.created_at, t.id) < (%s, %s)"
            + " order by t.created_at desc, t.id desc limit %s",
            (user_id, cursor.created_at, cursor.id, limit),
        ).fetchall()

    def update(self, trip_id: UUID, title: str, notify_email: bool) -> None:
        self._conn.execute(
            "update public.trips set title = %s, notify_email = %s where id = %s", (title, notify_email, trip_id)
        )

    def mark_processing(self, trip_id: UUID) -> None:
        self._conn.execute(
            "update public.trips set status = 'processing', submitted_at = now() where id = %s", (trip_id,)
        )

    def list_reel_keys(self, trip_id: UUID) -> list[str]:
        """R2 keys of rendered reels and posters, for deleting a trip."""
        rows = self._conn.execute(
            "select video_key as key from public.reels where trip_id = %s and video_key is not null"
            " union all "
            "select poster_key as key from public.reels where trip_id = %s and poster_key is not null",
            (trip_id, trip_id),
        ).fetchall()
        return [row["key"] for row in rows]

    def delete(self, trip_id: UUID) -> None:
        self._conn.execute("delete from public.trips where id = %s", (trip_id,))
