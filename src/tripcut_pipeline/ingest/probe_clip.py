import json
from pathlib import Path

from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.ingest.parse_frame_rate import parse_frame_rate
from tripcut_pipeline.ingest.read_first_tag import read_first_tag
from tripcut_pipeline.ingest.read_rotation import read_rotation
from tripcut_pipeline.tools.run_command import run_command


def probe_clip(path: Path, clip_id: str) -> ClipMeta:
    """Read duration, display size, codec, rotation, creation time and GPS with ffprobe."""
    output = run_command(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)]
    )
    info = json.loads(output)
    video = None
    has_audio = False
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video" and video is None:
            video = stream
        if stream.get("codec_type") == "audio":
            has_audio = True
    if video is None:
        raise ValueError(f"{path.name}: no video stream")

    rotation = read_rotation(video)
    width = int(video["width"])
    height = int(video["height"])
    if rotation in (90, 270):
        width, height = height, width

    fmt = info.get("format", {})
    duration_text = fmt.get("duration")
    if duration_text is None:
        duration_text = video.get("duration", "0")
    duration_s = float(duration_text)
    if duration_s <= 0.0:
        raise ValueError(f"{path.name}: zero duration")

    tags = dict(fmt.get("tags", {}))
    tags.update(video.get("tags", {}))
    creation_time = read_first_tag(tags, ("com.apple.quicktime.creationdate", "creation_time"))
    location = read_first_tag(tags, ("com.apple.quicktime.location.ISO6709", "location"))

    return ClipMeta(
        clip_id=clip_id,
        path=path,
        duration_s=duration_s,
        width=width,
        height=height,
        rotation=rotation,
        codec=str(video.get("codec_name", "unknown")),
        fps=parse_frame_rate(str(video.get("avg_frame_rate", "0/1"))),
        has_audio=has_audio,
        creation_time=creation_time,
        location=location,
    )
