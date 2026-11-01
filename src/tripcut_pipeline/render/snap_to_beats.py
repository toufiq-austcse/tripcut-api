from tripcut_pipeline.config.render_constants import MAX_SNAP_S, MIN_SHOT_S
from tripcut_pipeline.ingest.clip_meta import ClipMeta


def snap_to_beats(shots: list[dict], beat_times: list[float], clips: dict[str, ClipMeta]) -> list[dict]:
    """Move each cut to the nearest beat: shot lengths change so cut points land on the music grid.

    A cut moves at most 0.6 s; a shot never gets shorter than 0.6 s or longer than what is left of its clip.
    """
    if len(beat_times) == 0:
        return [dict(shot) for shot in shots]
    snapped = []
    reel_time = 0.0
    for shot in shots:
        start = float(shot["in"])
        length = float(shot["out"]) - start
        longest = clips[shot["clip_id"]].duration_s - start
        wanted_cut = reel_time + length
        best_cut = None
        for beat in beat_times:
            beat_length = beat - reel_time
            if beat_length < MIN_SHOT_S or beat_length > longest:
                continue
            if abs(beat - wanted_cut) > MAX_SNAP_S:
                continue
            if best_cut is None or abs(beat - wanted_cut) < abs(best_cut - wanted_cut):
                best_cut = beat
        if best_cut is not None:
            length = best_cut - reel_time
        new_shot = dict(shot)
        new_shot["out"] = round(start + length, 3)
        snapped.append(new_shot)
        reel_time += length
    return snapped
