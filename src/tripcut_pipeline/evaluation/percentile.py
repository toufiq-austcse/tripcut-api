def percentile(values: list[float], fraction: float) -> float:
    """Linear-interpolated percentile, fraction 0-1 (0.5 = median, 0.9 = p90)."""
    if len(values) == 0:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight
