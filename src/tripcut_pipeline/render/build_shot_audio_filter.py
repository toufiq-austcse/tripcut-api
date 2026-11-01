from tripcut_pipeline.config.render_constants import AUDIO_SAMPLE_RATE
from tripcut_pipeline.config.transition_constants import EDGE_FADE_S


def build_shot_audio_filter(exact_length: float) -> str:
    """ffmpeg -af for one shot: stereo 48 kHz, padded or trimmed to exactly the video length, 15 ms fade in/out.

    Same length as the video means the concat join has no gap (no held frame); the short edge fades stop clicks.
    """
    fade_out_start = max(0.0, exact_length - EDGE_FADE_S)
    return (
        f"aresample={AUDIO_SAMPLE_RATE},aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,"
        f"apad,atrim=0:{exact_length:.6f},"
        f"afade=t=in:d={EDGE_FADE_S},afade=t=out:st={fade_out_start:.6f}:d={EDGE_FADE_S}"
    )
