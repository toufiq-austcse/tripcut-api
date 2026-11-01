from tripcut_pipeline.config.director_constants import VERSION_SHOT_SECONDS
from tripcut_pipeline.config.transition_constants import VERSION_TRANSITION_SECONDS, VERSION_TRANSITIONS
from tripcut_pipeline.score.segment import Segment


def build_edit_list(
    version: str,
    title: str,
    shots: list[dict],
    segments_by_id: dict[str, Segment],
    duration_s: int,
    music_id: str | None,
) -> dict:
    """Director choice (segment ids) -> renderer contract (clip_id, in, out) per TDD-001 §8.4.

    Each shot takes the middle of its segment, up to the version's shot length, until the reel is full.
    """
    target = VERSION_SHOT_SECONDS[version]
    total = 0.0
    contract_shots = []
    for shot in shots:
        if total >= duration_s:
            break
        segment = segments_by_id[shot["segment_id"]]
        available = segment.end_s - segment.start_s
        length = min(target, available, duration_s - total)
        if length < 0.5:
            continue
        start = segment.start_s + (available - length) / 2
        crop = shot["crop"]
        if crop == "face" and len(segment.face_boxes) == 0:
            crop = "center"
        contract_shots.append(
            {
                "clip_id": segment.clip_id,
                "segment_id": segment.segment_id,
                "in": round(start, 3),
                "out": round(start + length, 3),
                "crop": crop,
                "text": None,
                "transition": VERSION_TRANSITIONS[version],
                "transition_s": VERSION_TRANSITION_SECONDS[version],
            }
        )
        total += length
    return {
        "version": version,
        "duration_s": duration_s,
        "music_id": music_id,
        "title": title,
        "shots": contract_shots,
    }
