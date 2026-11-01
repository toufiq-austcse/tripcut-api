# Music for the tripcut CLI

With `--music library` (the default) each reel uses the track for its mood below. `--music PATH`,
`--music-<version> PATH` and `--music none` override it (see `docs/runbooks/tripcut-cli.md`).
The file name without extension is the `music_id` in the edit lists.

| File | Reel | Original track | Source | License |
|------|------|----------------|--------|---------|
| `cc0_cinematic_calm.mp3` | `cinematic` | "Romantic Inspiration" (FreePD, category *romantic*) | <https://archive.org/download/freepd/romantic/Romantic%20Inspiration.mp3> | Public domain / CC0 |
| `cc0_fast_upbeat.mp3` | `fast` | "Funshine" (FreePD, category *upbeat*) | <https://archive.org/download/freepd/upbeat/Funshine.mp3> | Public domain / CC0 |
| `cc0_story_warm.mp3` | `story` | "Happy Whistling Ukulele" (FreePD, category *upbeat*) | <https://archive.org/download/freepd/upbeat/Happy%20Whistling%20Ukulele.mp3> | Public domain / CC0 |

**About the source.** FreePD.com published all its music as public domain (CC0) from 2008 to 2025, then
closed. The tracks above were downloaded on 2026-11-01 from the Internet Archive mirror of the site
(<https://archive.org/details/freepd>, uploaded 2022-03-18 while FreePD was still live, same category folders).

**What was changed:** the first 90 s of each track, a 3 s fade-out at the end, re-encoded to 160 kbps MP3,
metadata and cover art removed. The CLI loops the track if a reel is longer than 90 s.

SHA-256 of the original downloads:
- Romantic Inspiration: `5d96bd468d1edde0370c2a1d18e9fc5f6b8f208668a772537b7f145ddff8c445`
- Funshine: `b98b226927367a977377fe4f75d1cf59e4366ca2f444c2c7d23d13e7f506f532`
- Happy Whistling Ukulele: `ed4059c8fba8673d657e85175ff54eaa32cef9e43f688f164bef585e6e65cf15`

## Adding or swapping tracks

Only commit tracks that are CC0 / public domain. Add a row with the source URL and the license as shown on
the source page on the day you downloaded it. To change a reel's default track, change `LIBRARY_TRACKS` in
`src/tripcut_pipeline/config/music_constants.py`. Your own (licensed) songs: pass them with `--music PATH`
and keep them outside git. Any format FFmpeg can read works (mp3, m4a, wav, flac, ogg).
