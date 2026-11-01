import base64
import binascii
from datetime import datetime
from uuid import UUID

from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.api_error import ApiError
from tripcut_api.pagination.page_cursor import PageCursor


def decode_cursor(cursor: str) -> PageCursor:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
        created_at_text, id_text = raw.split("|", 1)
        return PageCursor(created_at=datetime.fromisoformat(created_at_text), id=UUID(id_text))
    except (binascii.Error, UnicodeError, ValueError) as error:
        raise ApiError(422, codes.VALIDATION_ERROR, "cursor: invalid value") from error
