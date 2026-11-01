from functools import lru_cache

from jwt import PyJWKClient

from tripcut_api.auth.jwt_constants import JWKS_CACHE_SECONDS, JWKS_PATH
from tripcut_api.config.get_settings import get_settings


@lru_cache(maxsize=1)
def get_jwk_client() -> PyJWKClient:
    settings = get_settings()
    jwks_url = settings.supabase_url.rstrip("/") + JWKS_PATH
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=JWKS_CACHE_SECONDS)
