from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MusicChoice:
    """The track one version uses: a file and where it came from (library / user), or no music (path None)."""

    version: str
    path: Path | None
    source: str
