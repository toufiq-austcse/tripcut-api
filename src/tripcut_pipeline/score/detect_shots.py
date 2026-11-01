from pathlib import Path

from scenedetect import ContentDetector, detect


def detect_shots(proxy_path: Path, duration_s: float) -> list[tuple[float, float]]:
    """PySceneDetect ContentDetector on the 360p proxy. A clip with no cut is one shot."""
    scenes = detect(str(proxy_path), ContentDetector())
    if len(scenes) == 0:
        return [(0.0, duration_s)]
    shots = []
    for start, end in scenes:
        shots.append((start.get_seconds(), end.get_seconds()))
    return shots
