from typing import Annotated

from fastapi import Depends

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.config.limits_constants import (
    ALLOWED_CONTENT_TYPE_PREFIX,
    MAX_CLIPS_PER_TRIP,
    MAX_OPEN_TRIPS,
    MAX_TRIP_BYTES,
    MIN_CLIPS_PER_TRIP,
)
from tripcut_api.config.upload_constants import MAX_PARTS_PER_SIGN, PART_SIZE_BYTES
from tripcut_api.schemas.me.limits_response import LimitsResponse
from tripcut_api.schemas.me.me_response import MeResponse


def get_me(user: Annotated[CurrentUser, Depends(get_current_user)]) -> MeResponse:
    """GET /v1/me: the signed-in user and the upload limits the client must follow."""
    limits = LimitsResponse(
        max_open_trips=MAX_OPEN_TRIPS,
        min_clips=MIN_CLIPS_PER_TRIP,
        max_clips=MAX_CLIPS_PER_TRIP,
        max_trip_bytes=MAX_TRIP_BYTES,
        part_size_bytes=PART_SIZE_BYTES,
        max_parts_per_sign=MAX_PARTS_PER_SIGN,
        allowed_content_type_prefix=ALLOWED_CONTENT_TYPE_PREFIX,
    )
    return MeResponse(id=user.id, email=user.email, limits=limits)
