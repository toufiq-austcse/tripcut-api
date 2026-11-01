from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from tripcut_api.auth.bearer_scheme_constants import BEARER_SCHEME
from tripcut_api.auth.current_user import CurrentUser
from tripcut_api.auth.get_jwk_client import get_jwk_client
from tripcut_api.auth.jwt_constants import ISSUER_PATH, JWT_ALGORITHMS, JWT_AUDIENCE
from tripcut_api.config.get_settings import get_settings
from tripcut_api.errors import error_codes_constants as codes
from tripcut_api.errors.api_error import ApiError


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(BEARER_SCHEME)],
) -> CurrentUser:
    """FastAPI dependency: verify the Supabase access token against the project's JWKS."""
    if credentials is None:
        raise ApiError(401, codes.UNAUTHORIZED, "Missing bearer token")

    token = credentials.credentials
    issuer = get_settings().supabase_url.rstrip("/") + ISSUER_PATH
    try:
        signing_key = get_jwk_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=JWT_ALGORITHMS,
            audience=JWT_AUDIENCE,
            issuer=issuer,
            options={"require": ["exp", "sub", "aud", "iss"]},
        )
        user_id = UUID(claims["sub"])
    except (jwt.PyJWTError, ValueError) as error:
        raise ApiError(401, codes.UNAUTHORIZED, "Invalid or expired token") from error

    email = None
    if "email" in claims:
        email = claims["email"]
    return CurrentUser(id=user_id, email=email)
