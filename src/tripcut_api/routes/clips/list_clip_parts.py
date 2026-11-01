from typing import Annotated
from uuid import UUID

from fastapi import Depends

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_clip_upload_service import get_clip_upload_service
from tripcut_api.schemas.clips.list_parts_response import ListPartsResponse
from tripcut_api.services.clip_upload_service import ClipUploadService


def list_clip_parts(
    clip_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ClipUploadService, Depends(get_clip_upload_service)],
) -> ListPartsResponse:
    """GET /v1/clips/{clip_id}/parts: the parts already in R2 (resume after a reload)."""
    return ListPartsResponse.model_validate(service.list_parts(user, clip_id))
