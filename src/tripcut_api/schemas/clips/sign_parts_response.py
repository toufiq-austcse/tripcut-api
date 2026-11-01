from pydantic import BaseModel

from tripcut_api.schemas.clips.signed_part_response import SignedPartResponse


class SignPartsResponse(BaseModel):
    parts: list[SignedPartResponse]
