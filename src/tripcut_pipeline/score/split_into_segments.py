import math

from tripcut_pipeline.config.score_constants import MAX_SEGMENT_S, MIN_SHOT_S


def split_into_segments(shots: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Cut each shot into equal pieces of at most 4 s; shots under 1 s are dropped."""
    bounds = []
    for start, end in shots:
        length = end - start
        if length < MIN_SHOT_S:
            continue
        pieces = max(1, math.ceil(length / MAX_SEGMENT_S))
        size = length / pieces
        for index in range(pieces):
            piece_start = start + index * size
            bounds.append((piece_start, piece_start + size))
    return bounds
