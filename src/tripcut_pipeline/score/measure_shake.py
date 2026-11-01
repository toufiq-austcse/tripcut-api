from pathlib import Path

import cv2
import numpy as np

from tripcut_pipeline.score.score_weights_constants import SHAKE_FULL_FRACTION


def measure_shake(frame_paths: list[Path]) -> float:
    """Stability 0-1 (1 = steady) from phase-correlation shifts between consecutive 2 fps frames."""
    if len(frame_paths) < 2:
        return 1.0
    previous = None
    shifts = []
    width = 1
    for path in frame_paths:
        gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            continue
        small = cv2.resize(gray, (160, max(1, int(gray.shape[0] * 160 / gray.shape[1]))))
        current = np.float32(small)
        width = current.shape[1]
        if previous is not None and previous.shape == current.shape:
            (dx, dy), _ = cv2.phaseCorrelate(previous, current)
            shifts.append(float(np.hypot(dx, dy)))
        previous = current
    if len(shifts) == 0:
        return 1.0
    fraction = float(np.mean(shifts)) / width
    return max(0.0, 1.0 - fraction / SHAKE_FULL_FRACTION)
