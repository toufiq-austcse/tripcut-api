import json
import logging

import anthropic

from tripcut_pipeline.config.director_constants import DIRECTOR_ATTEMPTS, DIRECTOR_EFFORT, DIRECTOR_MAX_TOKENS
from tripcut_pipeline.direct.build_director_content import build_director_content
from tripcut_pipeline.direct.build_edit_lists import build_edit_lists
from tripcut_pipeline.direct.director_prompt_constants import DIRECTOR_SYSTEM_PROMPT
from tripcut_pipeline.direct.director_request import DirectorRequest
from tripcut_pipeline.direct.director_result import DirectorResult
from tripcut_pipeline.direct.load_edit_list_schema import load_edit_list_schema
from tripcut_pipeline.direct.validate_director_output import validate_director_output
from tripcut_pipeline.errors.director_error import DirectorError


class ClaudeHaikuDirectorService:
    """Director on Claude Haiku 5.5: 60 keyframes + scores in, schema-checked JSON out, one retry."""

    def __init__(self, model: str) -> None:
        self._model = model
        try:
            self._client = anthropic.Anthropic()
        except anthropic.AnthropicError as error:
            raise DirectorError(f"cannot create Anthropic client: {error}") from error

    def direct(self, request: DirectorRequest) -> DirectorResult:
        log = logging.getLogger(__name__)
        content = build_director_content(request)
        schema = load_edit_list_schema()
        known_ids = {segment.segment_id for segment in request.segments}
        tokens_in = 0
        tokens_out = 0
        notes: list[str] = []
        for attempt in range(1, DIRECTOR_ATTEMPTS + 1):
            try:
                response = self._client.messages.create(
                    model=self._model,
                    max_tokens=DIRECTOR_MAX_TOKENS,
                    system=DIRECTOR_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": content}],
                    output_config={"effort": DIRECTOR_EFFORT, "format": {"type": "json_schema", "schema": schema}},
                )
            except anthropic.RateLimitError as error:
                raise DirectorError(f"rate limited: {error.message}", tokens_in, tokens_out) from error
            except anthropic.APIStatusError as error:
                raise DirectorError(
                    f"API error {error.status_code}: {error.message}", tokens_in, tokens_out
                ) from error
            except anthropic.APIConnectionError as error:
                raise DirectorError(f"network error: {error}", tokens_in, tokens_out) from error

            tokens_in += response.usage.input_tokens
            tokens_out += response.usage.output_tokens
            if response.stop_reason != "end_turn":
                notes.append(f"attempt {attempt}: stop_reason {response.stop_reason}")
                log.warning("director attempt %d stopped with %s", attempt, response.stop_reason)
                continue
            text = ""
            for block in response.content:
                if block.type == "text":
                    text = block.text
            try:
                output = json.loads(text)
                shots_by_version = validate_director_output(output, known_ids)
            except (json.JSONDecodeError, DirectorError) as error:
                notes.append(f"attempt {attempt}: invalid answer: {error}")
                log.warning("director attempt %d invalid: %s", attempt, error)
                continue
            title = str(output.get("title", request.trip_name)).strip()
            if title == "":
                title = request.trip_name
            return DirectorResult(
                edit_lists=build_edit_lists(request, title, shots_by_version),
                director="haiku",
                model=self._model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                attempts=attempt,
                notes=notes,
            )
        raise DirectorError("; ".join(notes), tokens_in, tokens_out)
