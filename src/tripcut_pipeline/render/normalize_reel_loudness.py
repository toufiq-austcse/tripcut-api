import logging
from pathlib import Path

from tripcut_pipeline.config.render_constants import AUDIO_BITRATE
from tripcut_pipeline.render.build_loudnorm_filter import build_loudnorm_filter
from tripcut_pipeline.render.measure_loudness import measure_loudness
from tripcut_pipeline.render.read_loudnorm_json import read_loudnorm_json
from tripcut_pipeline.tools.run_command_stderr import run_command_stderr


def normalize_reel_loudness(reel_path: Path, target_lufs: float, work_dir: Path) -> dict:
    """Set the reel's audio to target_lufs (two-pass loudnorm). The video stream is copied, not re-encoded.

    Replaces reel_path. Returns {"before_lufs", "after_lufs", "peak_db", "mode"} for the edit list / metrics.
    """
    log = logging.getLogger(__name__)
    stats = measure_loudness(reel_path, target_lufs)
    tmp_path = work_dir / f"{reel_path.stem}.loudnorm.mp4"
    args = [
        "ffmpeg", "-y", "-hide_banner", "-nostats", "-v", "info", "-i", str(reel_path),
        "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
        "-af", build_loudnorm_filter(stats, target_lufs),
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-movflags", "+faststart", str(tmp_path),
    ]
    values = read_loudnorm_json(args, run_command_stderr(args))
    tmp_path.replace(reel_path)
    result = {
        "before_lufs": round(float(stats.input_i), 1),
        "after_lufs": round(float(values["output_i"]), 1),
        "peak_db": round(float(values["output_tp"]), 1),
        "mode": values["normalization_type"],
    }
    log.info(
        "loudness %s: %.1f -> %.1f LUFS, peak %.1f dBFS (%s)",
        reel_path.name, result["before_lufs"], result["after_lufs"], result["peak_db"], result["mode"],
    )
    return result
