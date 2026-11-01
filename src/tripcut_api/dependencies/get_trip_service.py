from typing import Annotated

from fastapi import Depends
from psycopg import Connection

from tripcut_api.db.get_db_connection import get_db_connection
from tripcut_api.dependencies.get_r2_multipart_service import get_r2_multipart_service
from tripcut_api.repositories.clip_repository import ClipRepository
from tripcut_api.repositories.job_repository import JobRepository
from tripcut_api.repositories.trip_repository import TripRepository
from tripcut_api.repositories.user_repository import UserRepository
from tripcut_api.services.trip_service import TripService
from tripcut_api.storage.r2_multipart_service import R2MultipartService


def get_trip_service(
    conn: Annotated[Connection, Depends(get_db_connection)],
    storage: Annotated[R2MultipartService, Depends(get_r2_multipart_service)],
) -> TripService:
    return TripService(
        conn=conn,
        users=UserRepository(conn),
        trips=TripRepository(conn),
        clips=ClipRepository(conn),
        jobs=JobRepository(conn),
        storage=storage,
    )
