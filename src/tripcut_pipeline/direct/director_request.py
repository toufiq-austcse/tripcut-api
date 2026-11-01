from dataclasses import dataclass

from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.score.segment import Segment


@dataclass(frozen=True)
class DirectorRequest:
    """What every director gets: the kept segments (keyframes + scores), clip time/place, target length."""

    trip_name: str
    duration_s: int
    music_id: str | None
    segments: list[Segment]
    clips: dict[str, ClipMeta]
