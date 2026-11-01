from functools import lru_cache

from tripcut_api.config.settings import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
