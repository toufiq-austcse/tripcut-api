from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: UUID
    kind: Literal["analyze", "rerender"]
    status: Literal["queued", "running", "succeeded", "failed"]
    step: Literal["ingest", "score", "direct", "music", "render", "notify"] | None
    attempt: int
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
