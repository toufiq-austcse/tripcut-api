from tripcut_pipeline.config.render_constants import FACE_SMOOTHING
from tripcut_pipeline.score.face_box import FaceBox


def smooth_face_track(boxes: list[FaceBox]) -> list[tuple[float, float]]:
    """(time, centre x) of the largest face per frame, smoothed with an exponential moving average."""
    largest: dict[float, FaceBox] = {}
    for box in boxes:
        current = largest.get(box.time_s)
        if current is None or box.width * box.height > current.width * current.height:
            largest[box.time_s] = box
    track = []
    smoothed = None
    for time_s in sorted(largest):
        center_x = largest[time_s].center_x
        if smoothed is None:
            smoothed = center_x
        else:
            smoothed = FACE_SMOOTHING * center_x + (1.0 - FACE_SMOOTHING) * smoothed
        track.append((time_s, smoothed))
    return track
