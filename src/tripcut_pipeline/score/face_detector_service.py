from pathlib import Path

import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions

from tripcut_pipeline.config.model_constants import FACE_MODEL_FILE, FACE_MODEL_URL
from tripcut_pipeline.score.face_box import FaceBox
from tripcut_pipeline.tools.download_model_file import download_model_file


class FaceDetectorService:
    """MediaPipe BlazeFace (short range) on 360p proxy frames."""

    def __init__(self) -> None:
        model_path = download_model_file(FACE_MODEL_URL, FACE_MODEL_FILE)
        options = vision.FaceDetectorOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            min_detection_confidence=0.5,
        )
        self._detector = vision.FaceDetector.create_from_options(options)

    def detect(self, image_path: Path, time_s: float) -> list[FaceBox]:
        image = mp.Image.create_from_file(str(image_path))
        result = self._detector.detect(image)
        width = float(image.width)
        height = float(image.height)
        boxes = []
        for detection in result.detections:
            box = detection.bounding_box
            confidence = 0.0
            if len(detection.categories) > 0:
                confidence = float(detection.categories[0].score)
            boxes.append(
                FaceBox(
                    time_s=time_s,
                    center_x=(box.origin_x + box.width / 2) / width,
                    center_y=(box.origin_y + box.height / 2) / height,
                    width=box.width / width,
                    height=box.height / height,
                    confidence=confidence,
                )
            )
        return boxes

    def close(self) -> None:
        self._detector.close()
