from typing import Annotated
from uuid import UUID

from fastapi import Depends, Response

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.dependencies.get_trip_service import get_trip_service
from tripcut_api.services.trip_service import TripService


def delete_trip(
    trip_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
) -> Response:
    """DELETE /v1/trips/{trip_id}"""
    service.delete(user, trip_id)
    return Response(status_code=204)
