import argparse
import os
from pathlib import Path

from tripcut_pipeline.config.director_constants import DEFAULT_DIRECTOR, DEFAULT_MODEL, DIRECTOR_NAMES
from tripcut_pipeline.config.music_constants import DEFAULT_CLIP_VOLUME, DEFAULT_MUSIC_VOLUME, MUSIC_LIBRARY
from tripcut_pipeline.errors.bad_input_error import BadInputError
from tripcut_pipeline.pipeline_options import PipelineOptions
from tripcut_pipeline.resolve_volume import resolve_volume


def resolve_options(args: argparse.Namespace) -> PipelineOptions:
    """Apply env defaults: flag > env var > built-in default.

    --director > TRIPCUT_DIRECTOR > haiku; TRIPCUT_MODEL > claude-haiku-5-5; --music > TRIPCUT_MUSIC > library;
    --clip-volume > TRIPCUT_CLIP_VOLUME > 0.25; --music-volume > TRIPCUT_MUSIC_VOLUME > 1.0.
    """
    director = args.director
    if director is None:
        director = os.environ.get("TRIPCUT_DIRECTOR")
    if director is None or director == "":
        director = DEFAULT_DIRECTOR
    if director not in DIRECTOR_NAMES:
        raise BadInputError(f"TRIPCUT_DIRECTOR must be one of {DIRECTOR_NAMES}, got {director!r}")

    model = os.environ.get("TRIPCUT_MODEL")
    if model is None or model == "":
        model = DEFAULT_MODEL

    if args.duration < 5:
        raise BadInputError("--duration must be at least 5 seconds")

    music = args.music
    if music is None:
        music = os.environ.get("TRIPCUT_MUSIC")
    if music is None or music == "":
        music = MUSIC_LIBRARY
    version_music = {"cinematic": args.music_cinematic, "fast": args.music_fast, "story": args.music_story}
    clip_volume = resolve_volume(args.clip_volume, "--clip-volume", "TRIPCUT_CLIP_VOLUME", DEFAULT_CLIP_VOLUME)
    music_volume = resolve_volume(args.music_volume, "--music-volume", "TRIPCUT_MUSIC_VOLUME", DEFAULT_MUSIC_VOLUME)

    return PipelineOptions(
        trip_dir=Path(args.trip_dir).expanduser().resolve(),
        out_dir=Path(args.out).expanduser().resolve(),
        music=music,
        version_music=version_music,
        clip_volume=clip_volume,
        music_volume=music_volume,
        director=director,
        model=model,
        duration_s=args.duration,
        keep_proxies=args.keep_proxies,
    )
