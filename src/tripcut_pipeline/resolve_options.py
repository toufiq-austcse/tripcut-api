import argparse
import os
from pathlib import Path

from tripcut_pipeline.config.director_constants import DEFAULT_DIRECTOR, DEFAULT_MODEL, DIRECTOR_NAMES
from tripcut_pipeline.errors.bad_input_error import BadInputError
from tripcut_pipeline.pipeline_options import PipelineOptions


def resolve_options(args: argparse.Namespace) -> PipelineOptions:
    """Apply env defaults: --director > TRIPCUT_DIRECTOR > haiku; TRIPCUT_MODEL > claude-haiku-5-5."""
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

    return PipelineOptions(
        trip_dir=Path(args.trip_dir).expanduser().resolve(),
        out_dir=Path(args.out).expanduser().resolve(),
        music=args.music,
        director=director,
        model=model,
        duration_s=args.duration,
        keep_proxies=args.keep_proxies,
    )
