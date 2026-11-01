from tripcut_pipeline.score.face_box import FaceBox
from tripcut_pipeline.score.score_weights_constants import FACE_AREA_FULL


def measure_faces(boxes: list[FaceBox]) -> tuple[float, float]:
    """(most faces in one frame, face_size 0-1 from the largest face area)."""
    counts: dict[float, int] = {}
    largest = 0.0
    for box in boxes:
        counts[box.time_s] = counts.get(box.time_s, 0) + 1
        largest = max(largest, box.width * box.height)
    most = 0
    if len(counts) > 0:
        most = max(counts.values())
    return float(most), min(largest / FACE_AREA_FULL, 1.0)
