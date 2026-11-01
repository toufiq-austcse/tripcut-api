"""Where the CLI keeps downloaded models, cached beat grids and bundled music."""

from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "tripcut"
MODEL_DIR = CACHE_DIR / "models"
BEAT_CACHE_DIR = CACHE_DIR / "beats"
REPO_ROOT = Path(__file__).resolve().parents[3]
MUSIC_DIR = REPO_ROOT / "assets" / "music"
