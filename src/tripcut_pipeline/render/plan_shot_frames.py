from tripcut_pipeline.config.render_constants import OUTPUT_FPS


def plan_shot_frames(shots: list[dict]) -> list[int]:
    """Frame count to render for each shot (after extend_for_fades).

    Cut points are rounded on the reel's own timeline, not per shot, so rounding never adds up and every cut
    stays within half a frame of its beat. A crossfaded shot adds its overlap frames (head_s before "in",
    tail_s after "out").
    """
    frames = []
    reel_time = 0.0
    for shot in shots:
        head_s = float(shot["head_s"])
        tail_s = float(shot["tail_s"])
        length = float(shot["out"]) - float(shot["in"]) - head_s - tail_s
        start_frame = round(reel_time * OUTPUT_FPS)
        end_frame = round((reel_time + length) * OUTPUT_FPS)
        extra_frames = round(head_s * OUTPUT_FPS) + round(tail_s * OUTPUT_FPS)
        frames.append(max(1, end_frame - start_frame + extra_frames))
        reel_time += length
    return frames
