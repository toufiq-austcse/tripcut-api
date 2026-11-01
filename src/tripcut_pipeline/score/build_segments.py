from tripcut_pipeline.config.ingest_constants import FRAME_SAMPLE_FPS
from tripcut_pipeline.ingest.clip_proxy import ClipProxy
from tripcut_pipeline.score.detect_shots import detect_shots
from tripcut_pipeline.score.segment import Segment
from tripcut_pipeline.score.split_into_segments import split_into_segments


def build_segments(proxy: ClipProxy, first_number: int) -> list[Segment]:
    """Shots -> 2-4 s segments, each with its 2 fps frames and the frame nearest its middle."""
    shots = detect_shots(proxy.proxy_path, proxy.meta.duration_s)
    timed_frames = []
    for index, path in enumerate(proxy.frame_paths):
        timed_frames.append((index / FRAME_SAMPLE_FPS, path))

    segments = []
    number = first_number
    for start, end in split_into_segments(shots):
        frames = [(time_s, path) for time_s, path in timed_frames if start <= time_s < end]
        if len(frames) == 0:
            continue
        middle = (start + end) / 2
        keyframe = min(frames, key=lambda frame: abs(frame[0] - middle))
        segments.append(
            Segment(
                segment_id=f"S{number:03d}",
                clip_id=proxy.meta.clip_id,
                start_s=round(start, 3),
                end_s=round(end, 3),
                frames=frames,
                keyframe_path=keyframe[1],
            )
        )
        number += 1
    return segments
