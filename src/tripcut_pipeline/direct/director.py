from typing import Protocol

from tripcut_pipeline.direct.director_request import DirectorRequest
from tripcut_pipeline.direct.director_result import DirectorResult


class Director(Protocol):
    """Swappable director (TDD-002 §10.1). Week 2 adds a Gemini implementation for the A/B test."""

    def direct(self, request: DirectorRequest) -> DirectorResult:
        """Return three edit lists: cinematic, fast, story. Raise DirectorError if it cannot."""
        ...
