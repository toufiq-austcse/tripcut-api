from fastapi import Request
from fastapi.responses import JSONResponse

from tripcut_api.errors.api_error import ApiError
from tripcut_api.errors.build_error_response import build_error_response


def handle_api_error(request: Request, error: ApiError) -> JSONResponse:
    return build_error_response(error.status_code, error.code, error.message)
