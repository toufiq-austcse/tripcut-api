from pydantic import BaseModel, ConfigDict, Field


class CreateClipRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    size_bytes: int = Field(gt=0)
    # Client-made id for the same file on the same device, e.g. "name:size:lastModified". Used to resume.
    fingerprint: str = Field(min_length=1, max_length=300)
