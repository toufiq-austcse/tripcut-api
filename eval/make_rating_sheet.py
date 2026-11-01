"""Build the blind 1-5 rating sheet from out/<trip>/{cinematic,fast,story}.mp4.

Usage (from the repo root): uv run python eval/make_rating_sheet.py --raters alice,bob [--seed 48]
Raters watch out/blind/<trip>/A.mp4, B.mp4, C.mp4 and fill eval/rating_sheet.csv.
The label -> version key is out/blind/key.csv; open it only after rating.
"""

import argparse
from pathlib import Path

from tripcut_pipeline.evaluation.build_blind_sheet import build_blind_sheet


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the blind rating sheet")
    parser.add_argument("--out", default="out", help="output root with one folder per trip")
    parser.add_argument("--sheet", default="eval/rating_sheet.csv")
    parser.add_argument("--raters", default="rater1", help="comma-separated rater names")
    parser.add_argument("--seed", type=int, default=48)
    args = parser.parse_args()
    raters = [name.strip() for name in args.raters.split(",") if name.strip() != ""]
    key_path = build_blind_sheet(Path(args.out), Path(args.sheet), raters, args.seed)
    print(f"wrote {args.sheet}; key in {key_path} (do not share with raters)")


if __name__ == "__main__":
    main()
