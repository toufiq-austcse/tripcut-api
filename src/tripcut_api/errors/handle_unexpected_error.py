import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.build_error_response import build_error_response


def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    logging.getLogger("tripcut_api").exception("unhandled error on %s %s", request.method, request.url.path)
    return build_error_response(500, codes.INTERNAL_ERROR, "Internal server error")
