from uuid import UUID

from psycopg import Connection


class UserRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def ensure_and_lock(self, user_id: UUID, email: str | None) -> None:
        """Make sure the users row exists (the auth trigger normally creates it), then lock it.

        The lock serialises trip creation per user, so the open-trip limit cannot be raced.
        Call inside a transaction.
        """
        self._conn.execute(
            "insert into public.users (id, email) values (%s, %s) on conflict (id) do nothing",
            (user_id, email),
        )
        self._conn.execute("select id from public.users where id = %s for update", (user_id,))
