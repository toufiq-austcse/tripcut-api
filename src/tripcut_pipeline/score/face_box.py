from dataclasses import dataclass


@dataclass(frozen=True)
class FaceBox:
    """One detected face on a proxy frame. Centre and size are 0-1 fractions of the frame."""

    time_s: float
    center_x: float
    center_y: float
    width: float
    height: float
    confidence: float
