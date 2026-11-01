from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.score.segment import Segment


def describe_segment(segment: Segment, clip: ClipMeta) -> str:
    """One text line per segment for the director, placed just before its keyframe image."""
    filmed = "unknown time"
    if clip.creation_time is not None:
        filmed = clip.creation_time
    features = segment.features
    parts = [
        segment.segment_id,
        f"clip {segment.clip_id}",
        f"filmed {filmed}",
        f"{segment.end_s - segment.start_s:.1f} s",
        f"faces {int(features.get('faces', 0))}",
    ]
    for name in ("sharpness", "stability", "exposure", "aesthetic", "laughter", "cheer"):
        if name in features:
            parts.append(f"{name} {features[name]:.2f}")
    parts.append(f"score {segment.score:.2f}")
    return " | ".join(parts)
