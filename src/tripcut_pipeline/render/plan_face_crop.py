from tripcut_pipeline.config.render_constants import MAX_PAN_PX_PER_S, OUTPUT_HEIGHT, OUTPUT_WIDTH
from tripcut_pipeline.ingest.clip_meta import ClipMeta


def plan_face_crop(clip: ClipMeta, shot: dict, track: list[tuple[float, float]]) -> str:
    """FFmpeg scale+crop filter for a 9:16 1080x1920 frame.

    Landscape (or any frame wider than 9:16): scale to 1920 high and move a 1080-wide window.
    With crop "face" the window pans in a straight line from the smoothed face position at the
    shot's start to the one at its end (at most 400 px/s); with no face (or crop "center") it stays centred.
    Frames narrower than 9:16: scale to 1080 wide and crop the middle.
    """
    if clip.width * OUTPUT_HEIGHT < clip.height * OUTPUT_WIDTH:
        scaled_height = int(round(clip.height * OUTPUT_WIDTH / clip.width / 2)) * 2
        return f"scale={OUTPUT_WIDTH}:{scaled_height},crop={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:0:(ih-{OUTPUT_HEIGHT})/2"

    scaled_width = int(round(clip.width * OUTPUT_HEIGHT / clip.height / 2)) * 2
    span = max(0, scaled_width - OUTPUT_WIDTH)
    x_expression = f"{span / 2:.1f}"
    start = float(shot["in"])
    end = float(shot["out"])
    points = [(time_s, center_x) for time_s, center_x in track if start - 1.0 <= time_s <= end + 1.0]
    if shot["crop"] == "face" and len(points) > 0 and span > 0:
        first = min(points, key=lambda point: abs(point[0] - start))[1]
        last = min(points, key=lambda point: abs(point[0] - end))[1]
        x_start = min(max(first * scaled_width - OUTPUT_WIDTH / 2, 0.0), float(span))
        x_end = min(max(last * scaled_width - OUTPUT_WIDTH / 2, 0.0), float(span))
        duration = max(end - start, 0.1)
        max_pan = MAX_PAN_PX_PER_S * duration
        x_end = min(max(x_end, x_start - max_pan), x_start + max_pan)
        x_expression = f"'{x_start:.1f}+({x_end - x_start:.1f})*min(t/{duration:.3f},1)'"
    return f"scale={scaled_width}:{OUTPUT_HEIGHT},crop={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:{x_expression}:0"
