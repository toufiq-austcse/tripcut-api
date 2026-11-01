from tripcut_pipeline.config.order_constants import ORDER_MOOD
from tripcut_pipeline.score.segment import Segment


def fill_one_per_clip(shots: list[dict], segments_by_id: dict[str, Segment], order: str) -> list[dict]:
    """Put the director's picks in fill order so each clip is used once before any clip is used again (rev 7).

    Round 1: the first pick of each clip, in the director's priority. Round 2: the second pick of each clip, and
    so on. build_edit_list only reaches the later rounds when the reel is not full yet. With order mood the
    picks are returned as they are.
    """
    if order == ORDER_MOOD:
        return list(shots)
    rounds: list[list[dict]] = []
    picks_per_clip: dict[str, int] = {}
    for shot in shots:
        clip_id = segments_by_id[shot["segment_id"]].clip_id
        round_index = 0
        if clip_id in picks_per_clip:
            round_index = picks_per_clip[clip_id]
        picks_per_clip[clip_id] = round_index + 1
        if round_index == len(rounds):
            rounds.append([])
        rounds[round_index].append(shot)
    ordered = []
    for round_shots in rounds:
        ordered.extend(round_shots)
    return ordered
