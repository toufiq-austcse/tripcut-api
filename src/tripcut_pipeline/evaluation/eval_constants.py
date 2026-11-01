"""Eval set settings (TDD-002 §10.2)."""

STAGES = ("ingest", "score", "music", "direct", "render")
BLIND_LABELS = ("A", "B", "C")
TRIPS_CSV_COLUMNS = ("trip_id", "clips", "minutes", "codec", "max_res", "source_phone")
RATING_SHEET_COLUMNS = ("trip_id", "label", "file", "rater", "score_1_to_5", "note")
