from typing import Annotated
from uuid import UUID

from fastapi import Depends

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_trip_service import get_trip_service
from tripcut_api.schemas.trips.trip_response import TripResponse
from tripcut_api.schemas.trips.update_trip_request import UpdateTripRequest
from tripcut_api.services.trip_service import TripService


def update_trip(
    trip_id: UUID,
    body: UpdateTripRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> TripResponse:
    """PATCH /v1/trips/{trip_id}"""
    return TripResponse.model_validate(service.update(user, trip_id, body))
