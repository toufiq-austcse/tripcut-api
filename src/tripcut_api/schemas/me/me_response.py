from uuid import UUID

from pydantic import BaseModel

from tripcut_api.schemas.me.limits_response import LimitsResponse


class MeResponse(BaseModel):
    id: UUID
    email: str | None
    limits: LimitsResponse
