from uuid import UUID

from psycopg import Connection


class JobRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def insert_queued(self, trip_id: UUID, user_id: UUID, kind: str) -> None:
        self._conn.execute(
            "insert into public.jobs (trip_id, user_id, kind, status) values (%s, %s, %s, 'queued')",
            (trip_id, user_id, kind),
        )

    def latest_for_trip(self, trip_id: UUID) -> dict | None:
        return self._conn.execute(
            "select id, kind::text as kind, status::text as status, step::text as step, attempt, error,"
            " started_at, finished_at, created_at"
            " from public.jobs where trip_id = %s order by created_at desc, id desc limit 1",
            (trip_id,),
        ).fetchone()
