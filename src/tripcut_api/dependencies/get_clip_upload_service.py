from typing import Annotated

from fastapi import Depends
from psycopg import Connection

from tripcut_api.db.get_db_connection import get_db_connection
from tripcut_api.dependencies.get_r2_multipart_service import get_r2_multipart_service
from tripcut_api.repositories.clip_repository import ClipRepository
from tripcut_api.repositories.trip_repository import TripRepository
from tripcut_api.services.clip_upload_service import ClipUploadService
from tripcut_api.storage.r2_multipart_service import R2MultipartService


def get_clip_upload_service(
    conn: Annotated[Connection, Depends(get_db_connection)],
    storage: Annotated[R2MultipartService, Depends(get_r2_multipart_service)],
) -> ClipUploadService:
    return ClipUploadService(conn=conn, trips=TripRepository(conn), clips=ClipRepository(conn), storage=storage)
