"""Stage 3 (direct) settings: the three versions and the Claude call."""

VERSIONS = ("cinematic", "fast", "story")
VERSION_SHOT_COUNTS = {"cinematic": 9, "fast": 22, "story": 12}
VERSION_SHOT_SECONDS = {"cinematic": 3.4, "fast": 1.3, "story": 2.5}
DEFAULT_DIRECTOR = "haiku"
DIRECTOR_NAMES = ("haiku", "fallback")
DEFAULT_MODEL = "claude-haiku-5-5"
DIRECTOR_EFFORT = "medium"
DIRECTOR_MAX_TOKENS = 16000
DIRECTOR_ATTEMPTS = 2
KEYFRAME_WIDTH = 512
KEYFRAME_HEIGHT = 288
KEYFRAME_JPEG_QUALITY = 80
