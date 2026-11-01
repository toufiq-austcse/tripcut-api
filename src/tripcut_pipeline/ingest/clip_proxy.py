from dataclasses import dataclass
from pathlib import Path

from tripcut_pipeline.ingest.clip_meta import ClipMeta


@dataclass(frozen=True)
class ClipProxy:
    """The 360p working copy of one clip: small video, 2 fps JPEG frames, 16 kHz mono wav."""

    meta: ClipMeta
    proxy_path: Path
    frame_paths: list[Path]
    audio_path: Path | None
