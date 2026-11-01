from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineOptions:
    """CLI options after env defaults are applied."""

    trip_dir: Path
    out_dir: Path
    music: str
    version_music: dict[str, str | None]
    clip_volume: float
    music_volume: float
    transition: str
    loudness_target: float | None
    order: str
    director: str
    model: str
    duration_s: int
    keep_proxies: bool
