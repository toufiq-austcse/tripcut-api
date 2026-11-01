from typing import Annotated
from uuid import UUID

from fastapi import Depends, Response

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_clip_upload_service import get_clip_upload_service
from tripcut_api.services.clip_upload_service import ClipUploadService


def abort_clip(
    clip_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ClipUploadService, Depends(get_clip_upload_service)],
) -> Response:
    """DELETE /v1/clips/{clip_id}: abort the upload (or delete the object) and remove the clip."""
    service.abort(user, clip_id)
    return Response(status_code=204)
