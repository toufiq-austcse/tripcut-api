from pydantic import BaseModel

from tripcut_api.schemas.clips.uploaded_part_response import UploadedPartResponse


class ListPartsResponse(BaseModel):
    parts: list[UploadedPartResponse]
    uploaded_bytes: int
