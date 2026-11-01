from tripcut_pipeline.config.intro_outro_constants import (
    AUDIO_FADE_IN_S,
    INTRO_OUTRO_AUTO,
    INTRO_OUTRO_OFF,
    LAST_SHOT_MIN_S,
    VIDEO_FADE_IN_S,
    VIDEO_FADE_OUT_S,
)
from tripcut_pipeline.render.edge_fades import EdgeFades


def resolve_edge_fades(version: str, mode: str) -> EdgeFades:
    """The intro/outro of one version for --intro-outro auto|off (off = all zero)."""
    if mode == INTRO_OUTRO_OFF:
        return EdgeFades(video_in_s=0.0, audio_in_s=0.0, video_out_s=0.0, last_shot_s=0.0)
    if mode != INTRO_OUTRO_AUTO:
        raise ValueError(f"unknown intro/outro mode {mode!r}")
    return EdgeFades(
        video_in_s=VIDEO_FADE_IN_S[version],
        audio_in_s=AUDIO_FADE_IN_S[version],
        video_out_s=VIDEO_FADE_OUT_S[version],
        last_shot_s=LAST_SHOT_MIN_S[version],
    )
