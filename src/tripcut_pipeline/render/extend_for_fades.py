from tripcut_pipeline.config.render_constants import OUTPUT_FPS
from tripcut_pipeline.config.transition_constants import MIN_FADE_FRAMES, TRANSITION_CUT, TRANSITION_FADE
from tripcut_pipeline.ingest.clip_meta import ClipMeta


def extend_for_fades(shots: list[dict], clips: dict[str, ClipMeta]) -> list[dict]:
    """Give each crossfade its overlap without moving any beat-snapped cut point.

    The overlap comes first from footage before the incoming shot's "in" (head_s: the fade ends on the beat).
    If the clip starts too soon, the rest comes from footage after the previous shot's "out" (tail_s: the fade
    then runs across the beat). With less room in both, or a short shot (at most half of either shot), the
    fade gets shorter; below 3 frames it becomes a cut. Fade lengths are whole frames.
    Returns new shots; "in", "out", "transition_s", "head_s" and "tail_s" are what gets rendered.
    """
    extended = []
    for shot in shots:
        new_shot = dict(shot)
        new_shot["head_s"] = 0.0
        new_shot["tail_s"] = 0.0
        extended.append(new_shot)
    for index, shot in enumerate(extended):
        if shot["transition"] != TRANSITION_FADE or index == 0:
            shot["transition"] = TRANSITION_CUT
            shot["transition_s"] = 0.0
            continue
        previous = extended[index - 1]
        start = float(shot["in"])
        length = float(shot["out"]) - start
        previous_length = float(previous["out"]) - float(previous["in"]) - previous["head_s"]
        wanted_frames = int(min(float(shot["transition_s"]), length / 2, previous_length / 2) * OUTPUT_FPS)
        head_frames = min(wanted_frames, int(start * OUTPUT_FPS))
        previous_room = clips[previous["clip_id"]].duration_s - float(previous["out"])
        tail_frames = max(0, min(wanted_frames - head_frames, int(previous_room * OUTPUT_FPS) - 1))
        if head_frames + tail_frames < MIN_FADE_FRAMES:
            shot["transition"] = TRANSITION_CUT
            shot["transition_s"] = 0.0
            continue
        head_s = head_frames / OUTPUT_FPS
        tail_s = tail_frames / OUTPUT_FPS
        shot["in"] = round(start - head_s, 6)
        shot["head_s"] = round(head_s, 6)
        shot["transition_s"] = round(head_s + tail_s, 6)
        previous["out"] = round(float(previous["out"]) + tail_s, 6)
        previous["tail_s"] = round(tail_s, 6)
    return extended
