from pathlib import Path

from tripcut_pipeline.errors.bad_input_error import BadInputError


def resolve_user_track(path_arg: str) -> Path:
    """A music file the user passed with --music / --music-<version>; must exist."""
    path = Path(path_arg).expanduser()
    if not path.is_file():
        raise BadInputError(f"music file not found: {path}")
    return path
