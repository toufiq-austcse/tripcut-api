def measure_repeated_footage(shots: list[dict]) -> float:
    """Seconds of footage that more than one shot of the reel shows (plan rev 7 target: 0.0).

    Uses each rendered shot's "in"/"out" (after extend_for_fades, so crossfade heads and tails count) and adds up
    the overlap of every pair of shots from the same clip.
    """
    repeated = 0.0
    for index, shot in enumerate(shots):
        for other in shots[index + 1:]:
            if other["clip_id"] != shot["clip_id"]:
                continue
            overlap = min(float(shot["out"]), float(other["out"])) - max(float(shot["in"]), float(other["in"]))
            if overlap > 0.0:
                repeated += overlap
    return round(repeated, 3)
