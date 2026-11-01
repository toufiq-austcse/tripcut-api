from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.build_error_response import build_error_response


def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    messages = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"])
        messages.append(f"{location}: {item['msg']}")
    return build_error_response(422, codes.VALIDATION_ERROR, "; ".join(messages))
