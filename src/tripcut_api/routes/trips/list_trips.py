from typing import Annotated

from fastapi import Depends, Query

from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_current_user import get_current_user
from tripcut_api.config.pagination_constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from tripcut_api.dependencies.get_trip_service import get_trip_service
from tripcut_api.schemas.trips.trip_page_response import TripPageResponse
from tripcut_api.services.trip_service import TripService


def list_trips(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[TripService, Depends(get_trip_service)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    cursor: Annotated[str | None, Query(max_length=200)] = None,
) -> TripPageResponse:
    """GET /v1/trips: newest first, keyset paging on (created_at, id)."""
    return TripPageResponse.model_validate(service.list_page(user, limit, cursor))
