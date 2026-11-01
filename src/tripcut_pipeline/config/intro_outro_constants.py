"""Intro and outro of every reel (plan rev 8, section 11): fade in from black, held last shot, fade to black."""

INTRO_OUTRO_AUTO = "auto"
INTRO_OUTRO_OFF = "off"
INTRO_OUTRO_MODES = (INTRO_OUTRO_AUTO, INTRO_OUTRO_OFF)
DEFAULT_INTRO_OUTRO = INTRO_OUTRO_AUTO
VIDEO_FADE_IN_S = {"cinematic": 0.4, "fast": 0.2, "story": 0.4}
AUDIO_FADE_IN_S = {"cinematic": 0.5, "fast": 0.3, "story": 0.5}
LAST_SHOT_MIN_S = {"cinematic": 2.0, "fast": 1.5, "story": 2.0}
VIDEO_FADE_OUT_S = {"cinematic": 1.0, "fast": 0.6, "story": 1.0}
