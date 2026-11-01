import logging
from pathlib import Path

from tripcut_pipeline.errors.command_error import CommandError
from tripcut_pipeline.errors.render_error import RenderError
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.music.beat_grid import BeatGrid
from tripcut_pipeline.render.render_reel import render_reel
from tripcut_pipeline.render.smooth_face_track import smooth_face_track
from tripcut_pipeline.render.snap_to_beats import snap_to_beats
from tripcut_pipeline.score.face_box import FaceBox


def render_trip(
    edit_lists: list[dict],
    clips: dict[str, ClipMeta],
    face_boxes: dict[str, list[FaceBox]],
    beat_grid: BeatGrid | None,
    work_dir: Path,
    out_dir: Path,
) -> list[dict]:
    """Stage 5: snap cuts to beats, render cinematic.mp4 / fast.mp4 / story.mp4. Returns the snapped edit lists."""
    log = logging.getLogger(__name__)
    face_tracks = {clip_id: smooth_face_track(boxes) for clip_id, boxes in face_boxes.items()}
    beat_times: list[float] = []
    music_path = None
    if beat_grid is not None:
        beat_times = beat_grid.beat_times
        music_path = beat_grid.path

    rendered = []
    for edit_list in edit_lists:
        snapped = dict(edit_list)
        snapped["shots"] = snap_to_beats(edit_list["shots"], beat_times, clips)
        out_path = out_dir / f"{edit_list['version']}.mp4"
        try:
            length = render_reel(snapped, clips, face_tracks, music_path, work_dir, out_path)
        except CommandError as error:
            raise RenderError(f"{edit_list['version']}: {error}") from error
        snapped["rendered_s"] = round(length, 3)
        log.info("rendered %s (%d shots, %.1f s)", out_path.name, len(snapped["shots"]), length)
        rendered.append(snapped)
    return rendered
