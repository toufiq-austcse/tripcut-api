from pathlib import Path

from tripcut_pipeline.config.loudness_constants import LOUDNESS_RANGE_LU, LOUDNESS_TRUE_PEAK_DB
from tripcut_pipeline.render.loudness_stats import LoudnessStats
from tripcut_pipeline.render.read_loudnorm_json import read_loudnorm_json
from tripcut_pipeline.tools.run_command_stderr import run_command_stderr


def measure_loudness(reel_path: Path, target_lufs: float) -> LoudnessStats:
    """Loudnorm pass 1: measure the reel's audio only (-vn), write nothing."""
    loudnorm = f"loudnorm=I={target_lufs}:TP={LOUDNESS_TRUE_PEAK_DB}:LRA={LOUDNESS_RANGE_LU}:print_format=json"
    args = [
        "ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", str(reel_path),
        "-vn", "-af", loudnorm, "-f", "null", "-",
    ]
    values = read_loudnorm_json(args, run_command_stderr(args))
    return LoudnessStats(
        input_i=values["input_i"],
        input_tp=values["input_tp"],
        input_lra=values["input_lra"],
        input_thresh=values["input_thresh"],
        target_offset=values["target_offset"],
    )
