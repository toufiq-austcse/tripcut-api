import csv
from pathlib import Path

from tripcut_pipeline.evaluation.eval_constants import TRIPS_CSV_COLUMNS


def write_trips_csv(runs: list[dict], path: Path) -> None:
    """eval/trips.csv from the run metrics. Keeps a hand-filled source_phone column for known trips."""
    phones: dict[str, str] = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                phones[row["trip_id"]] = row.get("source_phone", "")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRIPS_CSV_COLUMNS)
        writer.writeheader()
        for run in runs:
            phone = ""
            if run["trip"] in phones:
                phone = phones[run["trip"]]
            writer.writerow(
                {
                    "trip_id": run["trip"],
                    "clips": run["clips"],
                    "minutes": round(float(run["footage_s"]) / 60.0, 1),
                    "codec": "/".join(run["codec"]),
                    "max_res": run["max_res"],
                    "source_phone": phone,
                }
            )
