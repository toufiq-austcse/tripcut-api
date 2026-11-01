from pathlib import Path

from tripcut_pipeline.config.music_constants import MUSIC_EXTENSIONS, NO_MUSIC
from tripcut_pipeline.config.paths_constants import MUSIC_DIR
from tripcut_pipeline.errors.bad_input_error import BadInputError


def resolve_music_track(music_arg: str | None) -> Path | None:
    """--music none -> no music; --music PATH -> that file; not set -> first track in assets/music."""
    if music_arg is not None:
        if music_arg == NO_MUSIC:
            return None
        path = Path(music_arg).expanduser()
        if not path.is_file():
            raise BadInputError(f"music file not found: {path}")
        return path
    if not MUSIC_DIR.is_dir():
        return None
    for path in sorted(MUSIC_DIR.iterdir()):
        if path.suffix.lower() in MUSIC_EXTENSIONS:
            return path
    return None
