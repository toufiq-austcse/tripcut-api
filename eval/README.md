# Eval set: 10 real trips + blind 1-5 rating (SAN-48, TDD-002 §10.2)

Footage never goes into git. `eval/trips/` and `out/` are in `.gitignore`.

```text
eval/trips/<trip_id>/*.mov|*.mp4    10 real trips, 10-100 phone clips each (originals, untouched)
        │
        │ (1) uv run python eval/run_all.py
        ▼
out/<trip_id>/cinematic.mp4 fast.mp4 story.mp4 edit_lists/*.json metrics.json
out/summary.md                      per-stage median / p90 core-seconds (post on SAN-48)
eval/trips.csv                      trip_id, clips, minutes, codec, max_res, source_phone (fill source_phone by hand)
        │
        │ (2) uv run python eval/make_rating_sheet.py --raters alice,bob
        ▼
out/blind/<trip_id>/A.mp4 B.mp4 C.mp4   versions shuffled per trip (seeded)
out/blind/key.csv                   label -> version (do not open before rating)
eval/rating_sheet.csv               trip_id, label, file, rater, score_1_to_5, note
```

## Rating rules

- Watch A, B and C of one trip in a row, on a phone if you can.
- Score each 1-5: 1 = would not post, 3 = OK after small fixes, 5 = would post as is.
- Note one reason per score (wrong clip choice, boring start, bad crop, cut off a face, ...).
- Do not open `out/blind/key.csv` until all scores are in.

Week-2 gate (TDD-002 §10.3): median score per version and the share of reels scored 4-5.
