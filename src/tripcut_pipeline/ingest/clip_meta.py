from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClipMeta:
    """ffprobe facts about one original clip. width/height are the display size (after rotation)."""

    clip_id: str
    path: Path
    duration_s: float
    width: int
    height: int
    rotation: int
    codec: str
    fps: float
    has_audio: bool
    creation_time: str | None
    location: str | None
