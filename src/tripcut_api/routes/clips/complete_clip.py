from typing import Annotated
from uuid import UUID

from fastapi import Depends

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_clip_upload_service import get_clip_upload_service
from tripcut_api.schemas.clips.clip_response import ClipResponse
from tripcut_api.services.clip_upload_service import ClipUploadService


def complete_clip(
    clip_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ClipUploadService, Depends(get_clip_upload_service)],
) -> ClipResponse:
    """POST /v1/clips/{clip_id}/complete: empty body; the server lists the parts itself."""
    return ClipResponse.model_validate(service.complete(user, clip_id))
