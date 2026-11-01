"""Joins between shots (plan rev 4, section 7).

A shot's "transition" is how it starts after the previous shot; the first shot's is always "cut".
"""

TRANSITION_AUTO = "auto"
TRANSITION_CUT = "cut"
TRANSITION_FADE = "fade"
TRANSITION_MODES = (TRANSITION_AUTO, TRANSITION_CUT, TRANSITION_FADE)
DEFAULT_TRANSITION = TRANSITION_AUTO
VERSION_TRANSITIONS = {"cinematic": TRANSITION_FADE, "fast": TRANSITION_CUT, "story": TRANSITION_FADE}
VERSION_TRANSITION_SECONDS = {"cinematic": 0.4, "fast": 0.0, "story": 0.3}
FADE_WHEN_FORCED_S = 0.3
MIN_FADE_FRAMES = 3
EDGE_FADE_S = 0.015
