import json

from tripcut_pipeline.errors.command_error import CommandError


def read_loudnorm_json(args: list[str], stderr: str) -> dict:
    """Pull the JSON block that loudnorm (print_format=json) writes at the end of ffmpeg's stderr."""
    start = stderr.rfind("{")
    end = stderr.rfind("}")
    if start == -1 or end < start:
        raise CommandError(args, 0, "loudnorm printed no JSON: " + stderr)
    try:
        return json.loads(stderr[start:end + 1])
    except json.JSONDecodeError as error:
        raise CommandError(args, 0, f"loudnorm JSON unreadable ({error}): " + stderr) from error
