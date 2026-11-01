from dataclasses import dataclass


@dataclass(frozen=True)
class CreateClipResult:
    """The clip row, and whether it was created now (201) or found again by fingerprint (200)."""

    clip: dict
    created: bool
