from typing import Annotated
from uuid import UUID

from fastapi import Depends

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_trip_service import get_trip_service
from tripcut_api.schemas.trips.trip_detail_response import TripDetailResponse
from tripcut_api.services.trip_service import TripService


def submit_trip(
    trip_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> TripDetailResponse:
    """POST /v1/trips/{trip_id}/submit: close uploads and queue the analyze job (202)."""
    return TripDetailResponse.model_validate(service.submit(user, trip_id))
