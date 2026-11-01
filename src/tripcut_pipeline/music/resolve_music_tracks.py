from tripcut_pipeline.config.director_constants import VERSIONS
from tripcut_pipeline.config.music_constants import (
    LIBRARY_TRACKS,
    MUSIC_LIBRARY,
    NO_MUSIC,
    SOURCE_LIBRARY,
    SOURCE_NONE,
    SOURCE_USER,
)
from tripcut_pipeline.config.paths_constants import MUSIC_DIR
from tripcut_pipeline.errors.bad_input_error import BadInputError
from tripcut_pipeline.music.music_choice import MusicChoice
from tripcut_pipeline.music.resolve_user_track import resolve_user_track


def resolve_music_tracks(music: str, version_music: dict[str, str | None]) -> dict[str, MusicChoice]:
    """Pick the track for each version, first match wins:

    (1) --music-<version> PATH -> that file (user)
    (2) --music none           -> no music, clip sound only
    (3) --music PATH           -> that file for all 3 versions (user)
    (4) --music library        -> the bundled CC0 track for the version's mood (library)
    """
    choices = {}
    for version in VERSIONS:
        version_path = version_music[version]
        if version_path is not None:
            choices[version] = MusicChoice(version, resolve_user_track(version_path), SOURCE_USER)
        elif music == NO_MUSIC:
            choices[version] = MusicChoice(version, None, SOURCE_NONE)
        elif music != MUSIC_LIBRARY:
            choices[version] = MusicChoice(version, resolve_user_track(music), SOURCE_USER)
        else:
            library_path = MUSIC_DIR / LIBRARY_TRACKS[version]
            if not library_path.is_file():
                raise BadInputError(f"bundled track missing: {library_path}")
            choices[version] = MusicChoice(version, library_path, SOURCE_LIBRARY)
    return choices
