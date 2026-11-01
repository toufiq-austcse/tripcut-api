from tripcut_pipeline.config.render_constants import MERGE_GAP_S


def merge_same_clip_neighbours(shots: list[dict]) -> list[dict]:
    """Join neighbouring shots from one clip that (almost) touch into one continuous shot (plan rev 7, section 10).

    Two neighbours merge when they come from the same clip and the next one starts less than MERGE_GAP_S after
    the previous one ends: the merged shot runs from the first "in" to the last "out", so there is no cut and no
    footage plays twice. It keeps the first segment_id and lists all of them in "merged_segment_ids".
    Neighbours with a larger gap stay apart (a forward jump cut). Returns new shots.
    """
    merged: list[dict] = []
    for shot in shots:
        if len(merged) > 0:
            previous = merged[-1]
            gap = float(shot["in"]) - float(previous["out"])
            if previous["clip_id"] == shot["clip_id"] and gap >= 0.0 and gap < MERGE_GAP_S:
                previous["out"] = shot["out"]
                if shot["crop"] == "face":
                    previous["crop"] = "face"
                if "merged_segment_ids" not in previous:
                    previous["merged_segment_ids"] = [previous["segment_id"]]
                previous["merged_segment_ids"].append(shot["segment_id"])
                continue
        merged.append(dict(shot))
    return merged
