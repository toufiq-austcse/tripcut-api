from dataclasses import dataclass


@dataclass(frozen=True)
class EdgeFades:
    """Intro and outro of one reel in seconds; all 0.0 = --intro-outro off (hard start and end)."""

    video_in_s: float
    audio_in_s: float
    video_out_s: float
    last_shot_s: float
