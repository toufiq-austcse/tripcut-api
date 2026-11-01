import os

from tripcut_pipeline.config.loudness_constants import (
    DEFAULT_LOUDNESS_LUFS,
    LOUDNESS_OFF,
    MAX_LOUDNESS_LUFS,
    MIN_LOUDNESS_LUFS,
)
from tripcut_pipeline.errors.bad_input_error import BadInputError


def resolve_loudness(flag_value: str | None) -> float | None:
    """--loudness > TRIPCUT_LOUDNESS > -16. Returns the target in LUFS, or None for "off"."""
    raw = flag_value
    source = "--loudness"
    if raw is None:
        raw = os.environ.get("TRIPCUT_LOUDNESS")
        source = "TRIPCUT_LOUDNESS"
    if raw is None or raw.strip() == "":
        return DEFAULT_LOUDNESS_LUFS
    text = raw.strip()
    if text.lower() == LOUDNESS_OFF:
        return None
    try:
        target = float(text)
    except ValueError as error:
        raise BadInputError(f"{source} must be a number in LUFS (e.g. -16) or 'off', got {raw!r}") from error
    if target < MIN_LOUDNESS_LUFS or target > MAX_LOUDNESS_LUFS:
        raise BadInputError(
            f"{source} must be between {MIN_LOUDNESS_LUFS} and {MAX_LOUDNESS_LUFS} LUFS, got {target}"
        )
    return target
