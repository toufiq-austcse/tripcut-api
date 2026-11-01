import csv
import random
import shutil
from pathlib import Path

from tripcut_pipeline.config.director_constants import VERSIONS
from tripcut_pipeline.evaluation.eval_constants import BLIND_LABELS, RATING_SHEET_COLUMNS


def build_blind_sheet(out_root: Path, sheet_path: Path, raters: list[str], seed: int) -> Path:
    """Copy each trip's 3 reels to out/blind/<trip>/A|B|C.mp4 in a shuffled order and write the sheet.

    The label -> version key goes to out/blind/key.csv (not in git); raters only see the sheet and A/B/C files.
    """
    blind_root = out_root / "blind"
    blind_root.mkdir(parents=True, exist_ok=True)
    key_rows = []
    sheet_rows = []
    for trip_dir in sorted(path for path in out_root.iterdir() if path.is_dir() and path.name != "blind"):
        reels = [trip_dir / f"{version}.mp4" for version in VERSIONS]
        if not all(reel.exists() for reel in reels):
            continue
        order = list(VERSIONS)
        random.Random(f"{seed}:{trip_dir.name}").shuffle(order)
        target_dir = blind_root / trip_dir.name
        target_dir.mkdir(parents=True, exist_ok=True)
        for label, version in zip(BLIND_LABELS, order):
            target = target_dir / f"{label}.mp4"
            shutil.copyfile(trip_dir / f"{version}.mp4", target)
            key_rows.append({"trip_id": trip_dir.name, "label": label, "version": version})
            for rater in raters:
                sheet_rows.append(
                    {
                        "trip_id": trip_dir.name,
                        "label": label,
                        "file": str(target.relative_to(out_root.parent)),
                        "rater": rater,
                        "score_1_to_5": "",
                        "note": "",
                    }
                )
    key_path = blind_root / "key.csv"
    with key_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("trip_id", "label", "version"))
        writer.writeheader()
        writer.writerows(key_rows)
    with sheet_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RATING_SHEET_COLUMNS)
        writer.writeheader()
        writer.writerows(sheet_rows)
    return key_path
