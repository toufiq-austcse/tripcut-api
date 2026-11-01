def hold_last_shot(shots: list[dict], clip_durations: dict[str, float], last_shot_s: float) -> list[dict]:
    """Make the last shot at least last_shot_s long, so the reel can fade out on it. Returns new shots.

    The shot only grows by moving its "out" later, and only as far as its clip has footage that no other shot
    of the same clip shows (plan rev 7: no moment plays twice). With less footage it grows as far as it can.
    Run after snap_to_beats (the reel's end is not on a beat) and before extend_for_fades.
    """
    held = [dict(shot) for shot in shots]
    if len(held) == 0 or last_shot_s <= 0.0:
        return held
    last = held[-1]
    start = float(last["in"])
    end = float(last["out"])
    if end - start >= last_shot_s:
        return held
    latest = clip_durations[last["clip_id"]]
    for other in held[:-1]:
        if other["clip_id"] != last["clip_id"]:
            continue
        other_start = float(other["in"])
        if other_start >= end:
            latest = min(latest, other_start)
    last["out"] = round(max(end, min(start + last_shot_s, latest)), 3)
    return held
