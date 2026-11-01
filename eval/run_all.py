"""Run the tripcut CLI on every trip in eval/trips/ and write out/summary.md + eval/trips.csv.

Usage (from the repo root): uv run python eval/run_all.py [--director haiku|fallback] [--music library|none|PATH]
    [--music-cinematic PATH] [--music-fast PATH] [--music-story PATH] [--clip-volume 0..1] [--music-volume 0..1]
    [--transition auto|cut|fade] [--loudness LUFS|off]
    [--order time|upload|mood]
"""

import argparse
import subprocess
import sys
from pathlib import Path

from tripcut_pipeline.evaluation.load_run_metrics import load_run_metrics
from tripcut_pipeline.evaluation.summarize_runs import summarize_runs
from tripcut_pipeline.evaluation.write_trips_csv import write_trips_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tripcut on all eval trips")
    parser.add_argument("--trips", default="eval/trips", help="folder with one sub-folder per trip")
    parser.add_argument("--out", default="out", help="output root")
    parser.add_argument("--director", default=None, choices=("haiku", "fallback"))
    parser.add_argument("--music", default=None, metavar="library|none|PATH")
    parser.add_argument("--music-cinematic", default=None, metavar="PATH")
    parser.add_argument("--music-fast", default=None, metavar="PATH")
    parser.add_argument("--music-story", default=None, metavar="PATH")
    parser.add_argument("--clip-volume", default=None, metavar="0..1")
    parser.add_argument("--music-volume", default=None, metavar="0..1")
    parser.add_argument("--transition", default=None, choices=("auto", "cut", "fade"))
    parser.add_argument("--loudness", default=None, metavar="LUFS|off")
    parser.add_argument("--order", default=None, choices=("time", "upload", "mood"))
    parser.add_argument("--skip-done", action="store_true", help="skip trips that already have metrics.json")
    args = parser.parse_args()

    trips_root = Path(args.trips)
    out_root = Path(args.out)
    trip_dirs = sorted(path for path in trips_root.iterdir() if path.is_dir())
    failures = []
    for trip_dir in trip_dirs:
        trip_out = out_root / trip_dir.name
        if args.skip_done and (trip_out / "metrics.json").exists():
            continue
        command = [sys.executable, "-m", "tripcut_pipeline", str(trip_dir), "--out", str(trip_out)]
        if args.director is not None:
            command += ["--director", args.director]
        pass_through = [
            ("--music", args.music),
            ("--music-cinematic", args.music_cinematic),
            ("--music-fast", args.music_fast),
            ("--music-story", args.music_story),
            ("--clip-volume", args.clip_volume),
            ("--music-volume", args.music_volume),
            ("--transition", args.transition),
            ("--loudness", args.loudness),
            ("--order", args.order),
        ]
        for flag, value in pass_through:
            if value is not None:
                command += [flag, value]
        print(f"== {trip_dir.name}", flush=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            failures.append(f"{trip_dir.name} (exit {completed.returncode})")

    runs = load_run_metrics(out_root)
    summary_path = out_root / "summary.md"
    summary_path.write_text(summarize_runs(runs), encoding="utf-8")
    write_trips_csv(runs, Path("eval/trips.csv"))
    print(f"wrote {summary_path} and eval/trips.csv ({len(runs)} trips)")
    if len(failures) > 0:
        print("failed: " + ", ".join(failures))
        sys.exit(1)


if __name__ == "__main__":
    main()
