from tripcut_pipeline.config.render_constants import OUTPUT_FPS
from tripcut_pipeline.render.edge_fades import EdgeFades


def build_edge_fade_filter(index: int, shot: dict, shot_count: int, frame_count: int, edges: EdgeFades) -> str:
    """Video filter tail for one shot: ",fade=t=in…" on the first shot, ",fade=t=out…" on the last, else "".

    Fades are whole frames and to/from black; the reel's first and last frames are fully black. A fade never covers the frames a crossfade shares with the next
    shot (tail_s) or the previous one (head_s), and never more than half of the shot's own frames.
    """
    head_frames = round(float(shot["head_s"]) * OUTPUT_FPS)
    tail_frames = round(float(shot["tail_s"]) * OUTPUT_FPS)
    own_frames = frame_count - head_frames - tail_frames
    parts = ""
    if index == 0:
        fade_in = min(round(edges.video_in_s * OUTPUT_FPS), own_frames // 2)
        if fade_in > 0:
            parts += f",fade=t=in:s=0:n={fade_in}"
    if index == shot_count - 1:
        fade_out = min(round(edges.video_out_s * OUTPUT_FPS), own_frames // 2)
        if fade_out > 0:
            parts += f",fade=t=out:s={frame_count - 1 - fade_out}:n={fade_out}"
    return parts
