import logging
import urllib.request
from pathlib import Path

from tripcut_pipeline.config.paths_constants import MODEL_DIR


def download_model_file(url: str, file_name: str) -> Path:
    """Download a model file once into ~/.cache/tripcut/models and return its path."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    target = MODEL_DIR / file_name
    if target.exists():
        return target
    logging.getLogger(__name__).info("downloading %s", url)
    partial = target.with_suffix(target.suffix + ".part")
    urllib.request.urlretrieve(url, partial)
    partial.rename(target)
    return target
