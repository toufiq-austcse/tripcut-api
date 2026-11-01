from typing import Annotated

from fastapi import Depends

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_trip_service import get_trip_service
from tripcut_api.schemas.trips.create_trip_request import CreateTripRequest
from tripcut_api.schemas.trips.trip_response import TripResponse
from tripcut_api.services.trip_service import TripService


def create_trip(
    body: CreateTripRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> TripResponse:
    """POST /v1/trips"""
    return TripResponse.model_validate(service.create(user, body.title))
