import base64
from pathlib import Path

import cv2

from tripcut_pipeline.config.director_constants import KEYFRAME_HEIGHT, KEYFRAME_JPEG_QUALITY, KEYFRAME_WIDTH


def encode_keyframe(path: Path) -> str:
    """Fit the keyframe inside 512x288, encode as JPEG, return base64 text for an image block."""
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"cannot read keyframe {path}")
    height, width = image.shape[:2]
    scale = min(KEYFRAME_WIDTH / width, KEYFRAME_HEIGHT / height)
    if scale < 1.0:
        size = (max(1, int(width * scale)), max(1, int(height * scale)))
        image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    ok, buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), KEYFRAME_JPEG_QUALITY])
    if not ok:
        raise ValueError(f"cannot encode keyframe {path}")
    return base64.standard_b64encode(buffer.tobytes()).decode("ascii")
