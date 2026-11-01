from tripcut_pipeline.config.render_constants import OUTPUT_FPS
from tripcut_pipeline.config.transition_constants import TRANSITION_FADE


def build_transition_filter(shots: list[dict], frame_counts: list[int]) -> str:
    """ffmpeg -filter_complex that joins shot inputs 0..N-1, output labels [v] (video) and [ca] (clip sound).

    A "fade" shot crossfades in over its transition_s (xfade + acrossfade, both overlap by the same frames);
    a "cut" shot is appended with concat. The overlap is head_s + tail_s (see extend_for_fades).
    """
    parts = []
    for index in range(len(shots)):
        parts.append(f"[{index}:v]setpts=PTS-STARTPTS,fps={OUTPUT_FPS}[sv{index}]")
        parts.append(f"[{index}:a]asetpts=PTS-STARTPTS[sa{index}]")
    video_label = "[sv0]"
    audio_label = "[sa0]"
    joined_frames = frame_counts[0]
    for index in range(1, len(shots)):
        shot = shots[index]
        next_video = f"[v{index}]"
        next_audio = f"[a{index}]"
        if index == len(shots) - 1:
            next_video = "[v]"
            next_audio = "[ca]"
        if shot["transition"] == TRANSITION_FADE:
            fade_frames = round(float(shot["transition_s"]) * OUTPUT_FPS)
            fade_s = fade_frames / OUTPUT_FPS
            offset_s = (joined_frames - fade_frames) / OUTPUT_FPS
            parts.append(
                f"{video_label}[sv{index}]xfade=transition=fade:duration={fade_s:.6f}:offset={offset_s:.6f}{next_video}"
            )
            parts.append(f"{audio_label}[sa{index}]acrossfade=d={fade_s:.6f}:c1=tri:c2=tri{next_audio}")
            joined_frames += frame_counts[index] - fade_frames
        else:
            parts.append(
                f"{video_label}{audio_label}[sv{index}][sa{index}]concat=n=2:v=1:a=1[cv{index}]{next_audio}"
            )
            parts.append(f"[cv{index}]fps={OUTPUT_FPS}{next_video}")
            joined_frames += frame_counts[index]
        video_label = next_video
        audio_label = next_audio
    if len(shots) == 1:
        parts.append("[sv0]null[v]")
        parts.append("[sa0]anull[ca]")
    return ";".join(parts)
