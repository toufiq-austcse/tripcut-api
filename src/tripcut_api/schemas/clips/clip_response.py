from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ClipResponse(BaseModel):
    id: UUID
    trip_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    fingerprint: str
    status: Literal["uploading", "uploaded"]
    part_size_bytes: int
    part_count: int
    uploaded_at: datetime | None
    created_at: datetime
