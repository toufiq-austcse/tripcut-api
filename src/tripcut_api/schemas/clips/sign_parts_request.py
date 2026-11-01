from pydantic import BaseModel, ConfigDict, Field

from tripcut_api.config.upload_constants import MAX_PARTS_PER_SIGN


class SignPartsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    part_numbers: list[int] = Field(min_length=1, max_length=MAX_PARTS_PER_SIGN)
