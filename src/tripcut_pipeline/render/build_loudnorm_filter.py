from tripcut_pipeline.config.loudness_constants import LOUDNESS_RANGE_LU, LOUDNESS_TRUE_PEAK_DB
from tripcut_pipeline.config.render_constants import AUDIO_SAMPLE_RATE
from tripcut_pipeline.render.loudness_stats import LoudnessStats


def build_loudnorm_filter(stats: LoudnessStats, target_lufs: float) -> str:
    """Loudnorm pass 2 filter: the pass-1 values, linear gain where the peak allows it, back to 48 kHz."""
    loudnorm = (
        f"loudnorm=I={target_lufs}:TP={LOUDNESS_TRUE_PEAK_DB}:LRA={LOUDNESS_RANGE_LU}"
        f":measured_I={stats.input_i}:measured_TP={stats.input_tp}:measured_LRA={stats.input_lra}"
        f":measured_thresh={stats.input_thresh}:offset={stats.target_offset}"
        ":linear=true:print_format=json"
    )
    return f"{loudnorm},aresample={AUDIO_SAMPLE_RATE}"
