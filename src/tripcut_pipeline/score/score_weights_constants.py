"""Hand-tuned scoring weights for the spike (TDD-002 §10.1). Sum of positive weights = 1.0."""

SCORE_WEIGHTS = {
    "aesthetic": 0.35,
    "sharpness": 0.15,
    "stability": 0.15,
    "exposure": 0.10,
    "face_size": 0.15,
    "laughter": 0.05,
    "cheer": 0.05,
}
WIND_PENALTY = 0.10
SHARPNESS_FULL_VARIANCE = 250.0
SHAKE_FULL_FRACTION = 0.08
FACE_AREA_FULL = 0.12
