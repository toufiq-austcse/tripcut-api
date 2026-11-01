def parse_frame_rate(text: str) -> float:
    """Turn an ffprobe rate such as '30000/1001' into frames per second (0.0 if unknown)."""
    if "/" not in text:
        return float(text)
    numerator, denominator = text.split("/", 1)
    if float(denominator) == 0.0:
        return 0.0
    return float(numerator) / float(denominator)
