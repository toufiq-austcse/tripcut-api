def count_same_clip_joins(shots: list[dict]) -> int:
    """Number of joins where the next shot comes from the same clip as the shot before it (a jump cut)."""
    joins = 0
    for index in range(1, len(shots)):
        if shots[index]["clip_id"] == shots[index - 1]["clip_id"]:
            joins += 1
    return joins
