from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.build_error_response import build_error_response


def handle_http_error(request: Request, error: HTTPException) -> JSONResponse:
    if error.status_code == 404:
        code = codes.NOT_FOUND
    elif error.status_code == 405:
        code = codes.METHOD_NOT_ALLOWED
    else:
        code = codes.HTTP_ERROR
    return build_error_response(error.status_code, code, str(error.detail))
