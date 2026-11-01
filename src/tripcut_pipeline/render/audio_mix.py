from dataclasses import dataclass


@dataclass(frozen=True)
class AudioMix:
    """Levels for the reel's sound: clip sound under the music, and the music itself (0..1 each)."""

    clip_volume: float
    music_volume: float
