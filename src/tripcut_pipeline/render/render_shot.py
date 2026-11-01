from pathlib import Path

from tripcut_pipeline.config.render_constants import (
    AUDIO_SAMPLE_RATE,
    OUTPUT_FPS,
    VIDEO_CRF,
    VIDEO_PRESET,
)
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.render.build_shot_audio_filter import build_shot_audio_filter
from tripcut_pipeline.tools.run_command import run_command


def render_shot(clip: ClipMeta, shot: dict, frame_count: int, crop_filter: str, out_path: Path) -> None:
    """Cut one shot from the original clip as exactly frame_count frames, crop to 9:16.

    Writes H.264 + PCM (.mov). Audio is cut to the same length as the video (silence if the clip has none),
    so joined shots have no gap. The last frame is repeated if the clip ends a frame early.
    """
    start = float(shot["in"])
    exact_length = frame_count / OUTPUT_FPS
    args = ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", str(clip.path)]
    audio_map = "0:a:0"
    if not clip.has_audio:
        args += ["-f", "lavfi", "-t", f"{exact_length:.6f}", "-i", f"anullsrc=r={AUDIO_SAMPLE_RATE}:cl=stereo"]
        audio_map = "1:a:0"
    args += [
        "-map", "0:v:0", "-map", audio_map,
        "-vf", f"setpts=PTS-STARTPTS,{crop_filter},fps={OUTPUT_FPS},setsar=1,format=yuv420p,"
               f"tpad=stop_mode=clone:stop=2",
        "-frames:v", str(frame_count),
        "-af", build_shot_audio_filter(exact_length),
        "-c:v", "libx264", "-preset", VIDEO_PRESET, "-crf", str(VIDEO_CRF),
        "-c:a", "pcm_s16le", str(out_path),
    ]
    run_command(args)
