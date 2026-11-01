from pydantic import BaseModel, ConfigDict, Field


class CreateTripRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
