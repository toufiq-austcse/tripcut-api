from tripcut_pipeline.score.score_weights_constants import SCORE_WEIGHTS, WIND_PENALTY


def compute_segment_score(features: dict[str, float]) -> float:
    """Weighted sum of the 0-1 features, minus a small penalty for wind noise."""
    total = 0.0
    for name, weight in SCORE_WEIGHTS.items():
        if name in features:
            total += weight * features[name]
    if "wind" in features:
        total -= WIND_PENALTY * features["wind"]
    return round(total, 4)
