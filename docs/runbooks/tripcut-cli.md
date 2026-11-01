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

Options: `--director haiku|fallback`, `--duration 30`, `--keep-proxies`, `--verbose`, plus the music and transition options below.
Env: `TRIPCUT_DIRECTOR` (default `haiku`), `TRIPCUT_MODEL` (default `claude-haiku-5-5`).

### Music (the user's choice)

For each reel, the first rule that matches wins:

| Flag | Result |
|------|--------|
| `--music-cinematic PATH`, `--music-fast PATH`, `--music-story PATH` | your track for that reel only |
| `--music none` | no music, clip sound only (at full level) |
| `--music PATH` | your track for all 3 reels |
| `--music library` (default) | bundled CC0 track for the reel's mood: calm / upbeat / warm (`assets/music/`) |
| `--clip-volume 0..1` | clip sound under the music, default `0.25`; `0` = music only |
| `--music-volume 0..1` | music level, default `1.0` |

Env fallbacks when a flag is not given: `TRIPCUT_MUSIC`, `TRIPCUT_CLIP_VOLUME`, `TRIPCUT_MUSIC_VOLUME`.
Cuts snap to the beats of each reel's own track. `metrics.json` → `stages.music.tracks` records the track,
its source (`library` / `user` / `none`) and tempo per reel.

```bash
uv run tripcut ./eval/trips/lisbon --out ./out/a                                   # bundled tracks, clips at 25 %
uv run tripcut ./eval/trips/lisbon --music ~/Music/song.mp3 --out ./out/c1          # one track for all 3
uv run tripcut ./eval/trips/lisbon --music-fast ~/Music/edm.mp3 --out ./out/c2      # only fast.mp4 changes
uv run tripcut ./eval/trips/lisbon --clip-volume 0 --out ./out/music-only           # no clip sound
uv run tripcut ./eval/trips/lisbon --music none --out ./out/clips-only              # no music
```
Only commit tracks that are CC0 / public domain (see `assets/music/LICENSE.md`); your own songs stay outside git.
### Transitions between shots

| Flag | cinematic | story | fast |
|------|-----------|-------|------|
| `--transition auto` (default) | 0.4 s crossfade | 0.3 s crossfade | cut |
| `--transition cut` | cut | cut | cut |
| `--transition fade` | 0.4 s crossfade | 0.3 s crossfade | 0.3 s crossfade |

Env fallback: `TRIPCUT_TRANSITION`. A crossfade ends on the shot's beat (the incoming shot starts a little
earlier in its clip). If the clip has no room for it, the fade gets shorter, or becomes a cut below 0.1 s.
Each shot is cut to an exact number of frames, so no join holds a frame. Crossfades encode the reel video
once more (more render CPU); a reel with only cuts is joined without a second encode.
`metrics.json` → `stages.render.transitions` records cut / fade per reel.

```bash
uv run tripcut ./eval/trips/lisbon --transition cut --out ./out/cuts                # plain cuts in all 3
```

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
