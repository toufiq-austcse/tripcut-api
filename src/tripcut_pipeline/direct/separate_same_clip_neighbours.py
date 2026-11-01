from tripcut_pipeline.score.segment import Segment


def separate_same_clip_neighbours(segments: list[Segment]) -> list[Segment]:
    """Reorder so no two neighbours come from the same clip, keeping the order otherwise (plan rev 4, 7.3).

    When a segment has the same clip as the one before it, the next later segment from another clip is
    moved up in front of it. If no such segment is left, the rest stays as it is.
    """
    ordered = list(segments)
    for index in range(1, len(ordered)):
        if ordered[index].clip_id != ordered[index - 1].clip_id:
            continue
        for later in range(index + 1, len(ordered)):
            if ordered[later].clip_id != ordered[index - 1].clip_id:
                ordered.insert(index, ordered.pop(later))
                break
    return ordered
