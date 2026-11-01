from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineOptions:
    """CLI options after env defaults are applied."""

    trip_dir: Path
    out_dir: Path
    music: str | None
    director: str
    model: str
    duration_s: int
    keep_proxies: bool
