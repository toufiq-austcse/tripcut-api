import cv2
import numpy as np

from tripcut_pipeline.score.score_weights_constants import SHARPNESS_FULL_VARIANCE


def measure_quality(image_bgr: np.ndarray) -> tuple[float, float]:
    """(sharpness, exposure), both 0-1. Sharpness = Laplacian variance; exposure = mid-grey, few clipped pixels."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    sharpness = min(variance / SHARPNESS_FULL_VARIANCE, 1.0)

    histogram = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    total = float(histogram.sum())
    mean = float(gray.mean()) / 255.0
    clipped = float(histogram[:5].sum() + histogram[251:].sum()) / total
    exposure = max(0.0, 1.0 - abs(mean - 0.45) * 2.0 - clipped)
    return sharpness, exposure
