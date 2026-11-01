from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from tripcut_pipeline.score.face_box import FaceBox


@dataclass
class Segment:
    """A 2-4 s piece of one clip, with its proxy frames and the scores the director sees."""

    segment_id: str
    clip_id: str
    start_s: float
    end_s: float
    frames: list[tuple[float, Path]]
    keyframe_path: Path
    features: dict[str, float] = field(default_factory=dict)
    face_boxes: list[FaceBox] = field(default_factory=list)
    embedding: np.ndarray | None = None
    score: float = 0.0
