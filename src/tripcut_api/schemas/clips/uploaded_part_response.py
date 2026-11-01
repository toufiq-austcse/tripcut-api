from pydantic import BaseModel


class UploadedPartResponse(BaseModel):
    part_number: int
    size_bytes: int
