from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from tripcut_api.app.app_lifespan import app_lifespan
from tripcut_api.app.register_routes import register_routes
from tripcut_api.config.get_settings import get_settings
from tripcut_api.errors.api_error import ApiError
from tripcut_api.errors.handle_api_error import handle_api_error
from tripcut_api.errors.handle_http_error import handle_http_error
from tripcut_api.errors.handle_unexpected_error import handle_unexpected_error
from tripcut_api.errors.handle_validation_error import handle_validation_error


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="TripCut API",
        version="0.1.0",
        lifespan=app_lifespan,
        openapi_url="/v1/openapi.json",
        docs_url="/v1/docs",
        redoc_url=None,
    )

    origins = []
    for origin in settings.web_origins.split(","):
        cleaned = origin.strip()
        if cleaned != "":
            origins.append(cleaned)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["authorization", "content-type"],
        max_age=3600,
    )

    app.add_exception_handler(ApiError, handle_api_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(HTTPException, handle_http_error)
    app.add_exception_handler(Exception, handle_unexpected_error)

    register_routes(app)
    return app
