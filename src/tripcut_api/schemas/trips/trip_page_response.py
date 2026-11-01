from pydantic import BaseModel

from tripcut_api.schemas.trips.trip_response import TripResponse


class TripPageResponse(BaseModel):
    items: list[TripResponse]
    next_cursor: str | None
