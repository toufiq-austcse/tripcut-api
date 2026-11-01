def order_shots(shots: list[dict]) -> list[dict]:
    """Put contract shots in timeline order (plan rev 6).

    Segment ids (S001, S002, ...) are numbered in clip order, then by time inside the clip, so sorting by
    the segment number gives the order of the day. The number is compared as an int, so S1000 sorts after S999.
    (render/apply_transition makes the first shot a cut.)
    """
    return sorted(shots, key=lambda shot: int(shot["segment_id"][1:]))
