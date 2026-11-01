import argparse
import os
from pathlib import Path

from tripcut_pipeline.config.director_constants import DEFAULT_DIRECTOR, DEFAULT_MODEL, DIRECTOR_NAMES
from tripcut_pipeline.config.intro_outro_constants import DEFAULT_INTRO_OUTRO, INTRO_OUTRO_MODES
from tripcut_pipeline.config.order_constants import DEFAULT_ORDER, ORDER_MODES
from tripcut_pipeline.config.transition_constants import DEFAULT_TRANSITION, TRANSITION_MODES
from tripcut_pipeline.config.music_constants import DEFAULT_CLIP_VOLUME, DEFAULT_MUSIC_VOLUME, MUSIC_LIBRARY
from tripcut_pipeline.errors.bad_input_error import BadInputError
from tripcut_pipeline.pipeline_options import PipelineOptions
from tripcut_pipeline.resolve_loudness import resolve_loudness
from tripcut_pipeline.resolve_volume import resolve_volume


def resolve_options(args: argparse.Namespace) -> PipelineOptions:
    """Apply env defaults: flag > env var > built-in default.

    --director > TRIPCUT_DIRECTOR > haiku; TRIPCUT_MODEL > claude-haiku-5-5; --music > TRIPCUT_MUSIC > library;
    --clip-volume > TRIPCUT_CLIP_VOLUME > 0.25; --music-volume > TRIPCUT_MUSIC_VOLUME > 1.0;
    --transition > TRIPCUT_TRANSITION > auto; --loudness > TRIPCUT_LOUDNESS > -16 (off = None);
    --order > TRIPCUT_ORDER > time; --intro-outro > TRIPCUT_INTRO_OUTRO > auto.
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

    transition = args.transition
    if transition is None:
        transition = os.environ.get("TRIPCUT_TRANSITION")
    if transition is None or transition == "":
        transition = DEFAULT_TRANSITION
    if transition not in TRANSITION_MODES:
        raise BadInputError(f"TRIPCUT_TRANSITION must be one of {TRANSITION_MODES}, got {transition!r}")

    loudness_target = resolve_loudness(args.loudness)

    order = args.order
    if order is None:
        order = os.environ.get("TRIPCUT_ORDER")
    if order is None or order == "":
        order = DEFAULT_ORDER
    if order not in ORDER_MODES:
        raise BadInputError(f"TRIPCUT_ORDER must be one of {ORDER_MODES}, got {order!r}")

    intro_outro = args.intro_outro
    if intro_outro is None:
        intro_outro = os.environ.get("TRIPCUT_INTRO_OUTRO")
    if intro_outro is None or intro_outro == "":
        intro_outro = DEFAULT_INTRO_OUTRO
    if intro_outro not in INTRO_OUTRO_MODES:
        raise BadInputError(f"TRIPCUT_INTRO_OUTRO must be one of {INTRO_OUTRO_MODES}, got {intro_outro!r}")

    return PipelineOptions(
        trip_dir=Path(args.trip_dir).expanduser().resolve(),
        out_dir=Path(args.out).expanduser().resolve(),
        music=music,
        version_music=version_music,
        clip_volume=clip_volume,
        music_volume=music_volume,
        transition=transition,
        loudness_target=loudness_target,
        order=order,
        intro_outro=intro_outro,
        director=director,
        model=model,
        duration_s=args.duration,
        keep_proxies=args.keep_proxies,
    )
