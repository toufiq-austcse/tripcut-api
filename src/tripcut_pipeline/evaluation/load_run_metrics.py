import json
from pathlib import Path


def load_run_metrics(out_root: Path) -> list[dict]:
    """metrics.json of every finished run under out/<trip>/ (runs with an error are skipped)."""
    runs = []
    for path in sorted(out_root.glob("*/metrics.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "error" in data:
            continue
        runs.append(data)
    return runs
