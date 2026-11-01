from collections.abc import Iterator

from fastapi import Request
from psycopg import Connection


def get_db_connection(request: Request) -> Iterator[Connection]:
    """FastAPI dependency: borrow one pooled connection for the request."""
    with request.app.state.db_pool.connection() as connection:
        yield connection
