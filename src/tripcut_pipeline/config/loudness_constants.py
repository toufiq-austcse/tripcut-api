"""Same loudness for every reel (plan rev 5, section 8): two-pass ffmpeg loudnorm on the reel audio."""

LOUDNESS_OFF = "off"
DEFAULT_LOUDNESS_LUFS = -16.0
LOUDNESS_TRUE_PEAK_DB = -2.0  # -1.5 left AAC overshoot at -0.9 dBFS on trip02 story
LOUDNESS_RANGE_LU = 11.0
MIN_LOUDNESS_LUFS = -30.0
MAX_LOUDNESS_LUFS = -9.0
