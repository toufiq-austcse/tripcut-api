from pydantic import BaseModel, ConfigDict, Field


class UpdateTripRequest(BaseModel):
    """Partial update. A field that is left out (or null) keeps its current value."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    notify_email: bool | None = None
