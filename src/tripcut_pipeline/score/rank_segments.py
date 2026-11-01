import numpy as np

from tripcut_pipeline.config.score_constants import DEDUPE_COSINE, MAX_SEGMENTS_PER_CLIP, TOP_SEGMENTS
from tripcut_pipeline.score.compute_segment_score import compute_segment_score
from tripcut_pipeline.score.segment import Segment


def rank_segments(segments: list[Segment]) -> list[Segment]:
    """Score every segment, then keep the best 60: skip near-duplicates (SigLIP cosine) and cap per clip."""
    for segment in segments:
        segment.score = compute_segment_score(segment.features)
    ordered = sorted(segments, key=lambda item: item.score, reverse=True)

    kept: list[Segment] = []
    per_clip: dict[str, int] = {}
    for candidate in ordered:
        if len(kept) >= TOP_SEGMENTS:
            break
        if per_clip.get(candidate.clip_id, 0) >= MAX_SEGMENTS_PER_CLIP:
            continue
        duplicate = False
        if candidate.embedding is not None:
            for other in kept:
                if other.embedding is None:
                    continue
                if float(np.dot(candidate.embedding, other.embedding)) >= DEDUPE_COSINE:
                    duplicate = True
                    break
        if duplicate:
            continue
        kept.append(candidate)
        per_clip[candidate.clip_id] = per_clip.get(candidate.clip_id, 0) + 1
    kept.sort(key=lambda item: item.segment_id)
    return kept
