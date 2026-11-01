from pydantic import BaseModel


class LimitsResponse(BaseModel):
    max_open_trips: int
    min_clips: int
    max_clips: int
    max_trip_bytes: int
    part_size_bytes: int
    max_parts_per_sign: int
    allowed_content_type_prefix: str
