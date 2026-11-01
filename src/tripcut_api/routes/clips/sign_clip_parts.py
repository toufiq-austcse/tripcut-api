from typing import Annotated
from uuid import UUID

from fastapi import Depends

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_clip_upload_service import get_clip_upload_service
from tripcut_api.schemas.clips.sign_parts_request import SignPartsRequest
from tripcut_api.schemas.clips.sign_parts_response import SignPartsResponse
from tripcut_api.services.clip_upload_service import ClipUploadService


def sign_clip_parts(
    clip_id: UUID,
    body: SignPartsRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ClipUploadService, Depends(get_clip_upload_service)],
) -> SignPartsResponse:
    """POST /v1/clips/{clip_id}/parts:sign: presigned PUT URLs, valid for 1 hour."""
    return SignPartsResponse.model_validate({"parts": service.sign_parts(user, clip_id, body.part_numbers)})
