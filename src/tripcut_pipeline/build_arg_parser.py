import argparse

from tripcut_pipeline.config.director_constants import DIRECTOR_NAMES
from tripcut_pipeline.config.render_constants import DEFAULT_DURATION_S


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tripcut",
        description="Turn a folder of trip clips into 3 vertical reels (cinematic, fast, story).",
    )
    parser.add_argument("trip_dir", metavar="TRIP_DIR", help="folder with the trip's .mov/.mp4 clips")
    parser.add_argument("--out", required=True, metavar="OUT_DIR", help="where reels, edit lists and metrics go")
    parser.add_argument("--music", default=None, metavar="PATH|none",
                        help="music file, or 'none'; default: first track in assets/music")
    parser.add_argument("--director", default=None, choices=DIRECTOR_NAMES,
                        help="default: $TRIPCUT_DIRECTOR, else haiku")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_S, help="reel length in seconds")
    parser.add_argument("--keep-proxies", action="store_true", help="keep OUT_DIR/work (proxies, frames, shots)")
    parser.add_argument("--verbose", action="store_true", help="debug logging")
    return parser
