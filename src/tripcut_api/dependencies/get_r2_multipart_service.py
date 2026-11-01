from fastapi import Request

from tripcut_api.storage.r2_multipart_service import R2MultipartService


def get_r2_multipart_service(request: Request) -> R2MultipartService:
    """FastAPI dependency: the one R2 service made at startup (see app_lifespan)."""
    return request.app.state.r2_multipart_service
