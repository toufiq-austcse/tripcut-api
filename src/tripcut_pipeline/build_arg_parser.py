import argparse

from tripcut_pipeline.config.director_constants import DIRECTOR_NAMES
from tripcut_pipeline.config.order_constants import ORDER_MODES
from tripcut_pipeline.config.render_constants import DEFAULT_DURATION_S
from tripcut_pipeline.config.transition_constants import TRANSITION_MODES


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tripcut",
        description="Turn a folder of trip clips into 3 vertical reels (cinematic, fast, story).",
    )
    parser.add_argument("trip_dir", metavar="TRIP_DIR", help="folder with the trip's .mov/.mp4 clips")
    parser.add_argument("--out", required=True, metavar="OUT_DIR", help="where reels, edit lists and metrics go")
    parser.add_argument("--music", default=None, metavar="library|none|PATH",
                        help="library = bundled CC0 track per version (default, or $TRIPCUT_MUSIC), "
                             "none = clip sound only, PATH = one file for all 3 reels")
    parser.add_argument("--music-cinematic", default=None, metavar="PATH", help="track for cinematic.mp4 only")
    parser.add_argument("--music-fast", default=None, metavar="PATH", help="track for fast.mp4 only")
    parser.add_argument("--music-story", default=None, metavar="PATH", help="track for story.mp4 only")
    parser.add_argument("--clip-volume", type=float, default=None,
                        help="clip sound under the music, 0..1 (default $TRIPCUT_CLIP_VOLUME, else 0.25)")
    parser.add_argument("--music-volume", type=float, default=None,
                        help="music level, 0..1 (default $TRIPCUT_MUSIC_VOLUME, else 1.0)")
    parser.add_argument("--transition", default=None, choices=TRANSITION_MODES,
                        help="auto = crossfade for cinematic/story, cut for fast (default, or $TRIPCUT_TRANSITION); "
                             "cut = plain cuts in all 3; fade = crossfades in all 3")
    parser.add_argument("--loudness", default=None, metavar="LUFS|off",
                        help="loudness of every reel in LUFS, e.g. -16 (default, or $TRIPCUT_LOUDNESS) or -14; "
                             "off = keep the raw mix")
    parser.add_argument("--order", default=None, choices=ORDER_MODES,
                        help="clip order in all 3 reels: time = capture time (default, or $TRIPCUT_ORDER), "
                             "upload = file-name order, mood = the director orders cinematic/fast by mood")
    parser.add_argument("--director", default=None, choices=DIRECTOR_NAMES,
                        help="default: $TRIPCUT_DIRECTOR, else haiku")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_S, help="reel length in seconds")
    parser.add_argument("--keep-proxies", action="store_true", help="keep OUT_DIR/work (proxies, frames, shots)")
    parser.add_argument("--verbose", action="store_true", help="debug logging")
    return parser
