from tripcut_pipeline.score.audio_event_constants import AUDIO_EVENT_GROUPS


def aggregate_audio_events(
    windows: list[tuple[float, dict[str, float]]], start_s: float, end_s: float
) -> dict[str, float]:
    """Highest score per event group among the audio windows that start inside the segment."""
    totals = {name: 0.0 for name in AUDIO_EVENT_GROUPS}
    for time_s, groups in windows:
        if start_s - 0.5 <= time_s < end_s:
            for name, value in groups.items():
                totals[name] = max(totals[name], value)
    return totals
