from pathlib import Path

from tripcut_pipeline.config.ingest_constants import (
    AUDIO_SAMPLE_RATE,
    FRAME_SAMPLE_FPS,
    PROXY_HEIGHT,
    PROXY_VIDEO_FPS,
)
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.ingest.clip_proxy import ClipProxy
from tripcut_pipeline.tools.run_command import run_command


def make_proxy(meta: ClipMeta, work_dir: Path) -> ClipProxy:
    """One ffmpeg decode of the original -> 360p proxy video, 2 fps JPEG frames, 16 kHz mono wav."""
    clip_dir = work_dir / meta.clip_id
    frames_dir = clip_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    proxy_path = clip_dir / "proxy.mp4"
    audio_path = clip_dir / "audio.wav"

    args = [
        "ffmpeg", "-y", "-v", "error", "-i", str(meta.path),
        "-map", "0:v:0", "-vf", f"scale=-2:{PROXY_HEIGHT},fps={PROXY_VIDEO_FPS}",
        "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", str(proxy_path),
        "-map", "0:v:0", "-vf", f"scale=-2:{PROXY_HEIGHT},fps={FRAME_SAMPLE_FPS}",
        "-q:v", "4", str(frames_dir / "%05d.jpg"),
    ]
    if meta.has_audio:
        args += ["-map", "0:a:0", "-ac", "1", "-ar", str(AUDIO_SAMPLE_RATE), str(audio_path)]
    run_command(args)

    frame_paths = sorted(frames_dir.glob("*.jpg"))
    proxy_audio = None
    if meta.has_audio and audio_path.exists():
        proxy_audio = audio_path
    return ClipProxy(meta=meta, proxy_path=proxy_path, frame_paths=frame_paths, audio_path=proxy_audio)
