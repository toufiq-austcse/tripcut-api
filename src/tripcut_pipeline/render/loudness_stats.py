from dataclasses import dataclass


@dataclass(frozen=True)
class LoudnessStats:
    """What loudnorm pass 1 measured on a reel's audio (fed back into pass 2 as measured_*)."""

    input_i: str
    input_tp: str
    input_lra: str
    input_thresh: str
    target_offset: str
