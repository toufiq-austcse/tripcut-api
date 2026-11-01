from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BeatGrid:
    """A music track and its beat times in seconds (librosa beat tracker)."""

    music_id: str
    path: Path
    tempo_bpm: float
    duration_s: float
    beat_times: list[float]
