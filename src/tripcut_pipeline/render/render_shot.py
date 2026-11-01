from pathlib import Path

from tripcut_pipeline.config.render_constants import (
    AUDIO_BITRATE,
    AUDIO_SAMPLE_RATE,
    OUTPUT_FPS,
    VIDEO_CRF,
    VIDEO_PRESET,
)
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.tools.run_command import run_command


def render_shot(clip: ClipMeta, shot: dict, crop_filter: str, out_path: Path) -> None:
    """Cut one shot from the original clip, crop to 9:16, encode H.264 + AAC (silent audio if none)."""
    start = float(shot["in"])
    length = float(shot["out"]) - start
    args = ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{length:.3f}", "-i", str(clip.path)]
    audio_map = "0:a:0"
    if not clip.has_audio:
        args += ["-f", "lavfi", "-t", f"{length:.3f}", "-i", f"anullsrc=r={AUDIO_SAMPLE_RATE}:cl=stereo"]
        audio_map = "1:a:0"
    args += [
        "-map", "0:v:0", "-map", audio_map,
        "-vf", f"{crop_filter},fps={OUTPUT_FPS},setsar=1,format=yuv420p",
        "-af", f"aresample={AUDIO_SAMPLE_RATE},aformat=channel_layouts=stereo",
        "-c:v", "libx264", "-preset", VIDEO_PRESET, "-crf", str(VIDEO_CRF),
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-shortest", str(out_path),
    ]
    run_command(args)
