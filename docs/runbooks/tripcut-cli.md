# Runbook: tripcut CLI (SAN-48 week-1 spike)

Local batch CLI. No server, no docker, no Modal. A person runs these steps.

```text
 (1) setup ──► (2) one trip ──► (3) all 10 trips ──► (4) rating sheet ──► (5) post numbers on SAN-48
```

## 1. Setup (once)

```bash
brew install ffmpeg                       # if missing; ffmpeg + ffprobe must be on PATH
git clone git@github.com:toufiq-austcse/tripcut-api.git && cd tripcut-api
uv sync --extra pipeline                  # ML deps; API-only installs keep using plain `uv sync`
export ANTHROPIC_API_KEY=...              # paid-tier key (TDD-002 decision 5)
```

The first run downloads models to `~/.cache/tripcut/` (SigLIP ViT-B-16 ~800 MB, BlazeFace, YAMNet).

## 2. One trip

```bash
uv run tripcut ./eval/trips/lisbon --out ./out/lisbon
```

| Output | What |
|--------|------|
| `out/lisbon/cinematic.mp4`, `fast.mp4`, `story.mp4` | 1080x1920 H.264/AAC, ~30 s |
| `out/lisbon/edit_lists/<version>.json` | edit list as rendered (cuts snapped to beats) |
| `out/lisbon/edit_lists/<version>.director.json` | edit list as the director returned it |
| `out/lisbon/metrics.json` | per stage: wall_s, core_s, peak_rss_mb (+ tokens for `direct`) |

Options: `--music PATH|none`, `--director haiku|fallback`, `--duration 30`, `--keep-proxies`, `--verbose`.
Env: `TRIPCUT_DIRECTOR` (default `haiku`), `TRIPCUT_MODEL` (default `claude-haiku-5-5`).
If the Claude call fails or returns an invalid answer twice, the CLI uses the no-LLM fallback and sets
`stages.direct.fallback = true` with the reason.

Exit codes: `0` = 3 reels written, `2` = bad input (no readable clips, bad option), `3` = render failed.

## 3. All 10 trips

```bash
uv run python eval/run_all.py             # add --skip-done to resume
```

Writes `out/summary.md` and `eval/trips.csv`. Post `out/summary.md` as a comment on SAN-48.

Core-seconds here are from this machine (`metrics.json` → `machine`), not Modal x86.
Close other heavy apps while measuring.

## 4. Rating sheet

```bash
uv run python eval/make_rating_sheet.py --raters alice,bob
```

See `eval/README.md` for the rating rules. Commit `eval/trips.csv` and the filled `eval/rating_sheet.csv`;
never commit footage or `out/`.

## Rollback

Nothing is deployed. To remove the extra packages: `uv sync` (without `--extra pipeline`).
