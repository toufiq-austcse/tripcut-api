from datetime import datetime

from pydantic import BaseModel


class SignedPartResponse(BaseModel):
    part_number: int
    url: str
    expires_at: datetime
