from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from tripcut_api.config.get_settings import get_settings
from tripcut_api.db.create_db_pool import create_db_pool
from tripcut_api.storage.create_r2_client import create_r2_client
from tripcut_api.storage.r2_multipart_service import R2MultipartService


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open the DB pool and the R2 client once per container; close the pool on shutdown."""
    settings = get_settings()
    app.state.db_pool = create_db_pool(settings.supabase_db_url)
    app.state.r2_multipart_service = R2MultipartService(create_r2_client(settings), settings.r2_bucket)
    try:
        yield
    finally:
        app.state.db_pool.close()
