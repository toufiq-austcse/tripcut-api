import logging
import sys

from tripcut_pipeline.build_arg_parser import build_arg_parser
from tripcut_pipeline.config.exit_codes_constants import EXIT_BAD_INPUT
from tripcut_pipeline.errors.bad_input_error import BadInputError
from tripcut_pipeline.resolve_options import resolve_options
from tripcut_pipeline.run_pipeline import run_pipeline


def main() -> None:
    """Entry point for `tripcut TRIP_DIR --out OUT_DIR` (pyproject [project.scripts])."""
    args = build_arg_parser().parse_args()
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        options = resolve_options(args)
    except BadInputError as error:
        logging.getLogger(__name__).error("%s", error)
        sys.exit(EXIT_BAD_INPUT)
    sys.exit(run_pipeline(options))
