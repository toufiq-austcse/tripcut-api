from dataclasses import dataclass

from tripcut_pipeline.score.face_box import FaceBox
from tripcut_pipeline.score.segment import Segment


@dataclass(frozen=True)
class ScoreResult:
    """Stage 2 output: the kept top segments plus every face seen per clip (for the crop path)."""

    segment_count: int
    kept: list[Segment]
    face_tracks: dict[str, list[FaceBox]]
