from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class TripResponse(BaseModel):
    id: UUID
    title: str
    status: Literal["open", "processing", "ready", "failed"]
    notify_email: bool
    clip_count: int
    total_bytes: int
    uploaded_clip_count: int
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime
