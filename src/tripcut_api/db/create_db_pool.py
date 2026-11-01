from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


def create_db_pool(conninfo: str) -> ConnectionPool:
    """Pool of autocommit connections. Services open explicit transactions with conn.transaction().

    prepare_threshold=None turns off server-side prepared statements, so both the Supabase
    session pooler (5432) and transaction pooler (6543) work.
    """
    return ConnectionPool(
        conninfo,
        min_size=1,
        max_size=5,
        kwargs={"autocommit": True, "row_factory": dict_row, "prepare_threshold": None},
        open=True,
    )
