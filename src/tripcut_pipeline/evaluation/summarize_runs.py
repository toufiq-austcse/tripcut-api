from tripcut_pipeline.evaluation.eval_constants import STAGES
from tripcut_pipeline.evaluation.percentile import percentile


def summarize_runs(runs: list[dict]) -> str:
    """Markdown for SAN-48: per stage median / p90 core-seconds per trip and per footage minute."""
    machine = "n/a"
    if len(runs) > 0:
        machine = runs[0]["machine"]
    lines = [
        "# tripcut CLI: measured cost per trip",
        "",
        f"Trips: {len(runs)}. Machine: {machine}",
        "",
        "| Stage | median core-s / trip | p90 core-s / trip | median core-s / footage min | median wall s |",
        "|---|---:|---:|---:|---:|",
    ]
    totals = [0.0 for _ in runs]
    for stage in STAGES:
        per_trip = []
        per_minute = []
        wall = []
        for index, run in enumerate(runs):
            if stage not in run["stages"]:
                continue
            core = float(run["stages"][stage]["core_s"])
            per_trip.append(core)
            wall.append(float(run["stages"][stage]["wall_s"]))
            minutes = float(run["footage_s"]) / 60.0
            if minutes > 0:
                per_minute.append(core / minutes)
            totals[index] += core
        lines.append(
            f"| {stage} | {percentile(per_trip, 0.5):.1f} | {percentile(per_trip, 0.9):.1f} "
            f"| {percentile(per_minute, 0.5):.1f} | {percentile(wall, 0.5):.1f} |"
        )
    lines.append(
        f"| **total** | **{percentile(totals, 0.5):.1f}** | **{percentile(totals, 0.9):.1f}** | | |"
    )
    lines += [
        "",
        "## Per trip",
        "",
        "| Trip | clips | footage min | max res | core-s total | director | tokens in / out | fallback |",
        "|---|---:|---:|---|---:|---|---|---|",
    ]
    for index, run in enumerate(runs):
        direct = run["stages"].get("direct", {})
        lines.append(
            f"| {run['trip']} | {run['clips']} | {float(run['footage_s']) / 60.0:.1f} | {run['max_res']} "
            f"| {totals[index]:.1f} | {direct.get('model', 'fallback')} "
            f"| {direct.get('tokens_in', 0)} / {direct.get('tokens_out', 0)} | {direct.get('fallback', False)} |"
        )
    lines += ["", "Core-seconds = user+sys CPU of the CLI and its ffmpeg children (getrusage). Not Modal x86."]
    return "\n".join(lines) + "\n"
