import dataclasses
import logging

from tripcut_pipeline.direct.claude_haiku_director_service import ClaudeHaikuDirectorService
from tripcut_pipeline.direct.director import Director
from tripcut_pipeline.direct.director_request import DirectorRequest
from tripcut_pipeline.direct.director_result import DirectorResult
from tripcut_pipeline.direct.fallback_director_service import FallbackDirectorService
from tripcut_pipeline.errors.director_error import DirectorError


def direct_trip(request: DirectorRequest, director_name: str, model: str) -> DirectorResult:
    """Stage 3: ask the chosen director; on any director error use the deterministic fallback."""
    if director_name == "fallback":
        return FallbackDirectorService().direct(request)
    try:
        director: Director = ClaudeHaikuDirectorService(model)
        return director.direct(request)
    except DirectorError as error:
        logging.getLogger(__name__).warning("director failed, using fallback: %s", error)
        result = FallbackDirectorService().direct(request)
        return dataclasses.replace(
            result,
            fallback=True,
            fallback_reason=str(error),
            model=model,
            tokens_in=error.tokens_in,
            tokens_out=error.tokens_out,
        )
