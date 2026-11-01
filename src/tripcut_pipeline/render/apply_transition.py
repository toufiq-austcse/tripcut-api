from tripcut_pipeline.config.transition_constants import (
    FADE_WHEN_FORCED_S,
    TRANSITION_AUTO,
    TRANSITION_CUT,
    TRANSITION_FADE,
    VERSION_TRANSITION_SECONDS,
    VERSION_TRANSITIONS,
)


def apply_transition(edit_list: dict, mode: str) -> list[dict]:
    """Set "transition" + "transition_s" on every shot from --transition auto|cut|fade. Returns new shots.

    auto = the version's own choice (fade for cinematic/story, cut for fast); cut = cuts everywhere;
    fade = crossfades everywhere (fast, which has no fade length of its own, gets 0.3 s). The first shot is a cut.
    """
    version = edit_list["version"]
    transition = VERSION_TRANSITIONS[version]
    seconds = VERSION_TRANSITION_SECONDS[version]
    if mode == TRANSITION_CUT:
        transition = TRANSITION_CUT
        seconds = 0.0
    elif mode == TRANSITION_FADE:
        transition = TRANSITION_FADE
        if seconds <= 0.0:
            seconds = FADE_WHEN_FORCED_S
    elif mode != TRANSITION_AUTO:
        raise ValueError(f"unknown transition mode {mode!r}")
    if transition == TRANSITION_CUT:
        seconds = 0.0
    shots = []
    for index, shot in enumerate(edit_list["shots"]):
        new_shot = dict(shot)
        new_shot["transition"] = transition
        new_shot["transition_s"] = seconds
        if index == 0:
            new_shot["transition"] = TRANSITION_CUT
            new_shot["transition_s"] = 0.0
        shots.append(new_shot)
    return shots
