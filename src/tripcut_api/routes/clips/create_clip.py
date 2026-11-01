from typing import Annotated
from uuid import UUID

from fastapi import Depends, Response

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_clip_upload_service import get_clip_upload_service
from tripcut_api.schemas.clips.clip_response import ClipResponse
from tripcut_api.schemas.clips.create_clip_request import CreateClipRequest
from tripcut_api.services.clip_upload_service import ClipUploadService


def create_clip(
    trip_id: UUID,
    body: CreateClipRequest,
    response: Response,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ClipUploadService, Depends(get_clip_upload_service)],
) -> ClipResponse:
    """POST /v1/trips/{trip_id}/clips: 201 new clip, or 200 when the fingerprint is known (resume)."""
    result = service.create_clip(user, trip_id, body)
    if result.created:
        response.status_code = 201
    else:
        response.status_code = 200
    return ClipResponse.model_validate(result.clip)
