# Music for the tripcut CLI

The CLI uses the first track in this folder (sorted by name) unless `--music PATH` or `--music none` is given.
The track's file name (without extension) is the `music_id` in the edit lists.

| File | Source | License |
|------|--------|---------|
| `tripcut_pulse_120bpm.m4a` | Made for this repo with ffmpeg `aevalsrc` (a 120 BPM sine kick and pad, 40 s). No samples from other works. | CC0 1.0, dedicated to the public domain by the TripCut team |

## Adding CC0 tracks

Only add tracks that are CC0 / public domain (TDD-002: music library is 1-3 CC0 tracks in the spike).
For each track, add a row with the source URL and the license as shown on the source page on the day you downloaded it.
Any format FFmpeg can read works (mp3, m4a, wav, flac, ogg).
