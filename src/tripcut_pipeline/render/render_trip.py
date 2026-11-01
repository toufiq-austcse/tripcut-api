import logging
from pathlib import Path

from tripcut_pipeline.errors.command_error import CommandError
from tripcut_pipeline.errors.render_error import RenderError
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.music.beat_grid import BeatGrid
from tripcut_pipeline.render.apply_transition import apply_transition
from tripcut_pipeline.render.audio_mix import AudioMix
from tripcut_pipeline.render.extend_for_fades import extend_for_fades
from tripcut_pipeline.render.hold_last_shot import hold_last_shot
from tripcut_pipeline.render.merge_same_clip_neighbours import merge_same_clip_neighbours
from tripcut_pipeline.render.normalize_reel_loudness import normalize_reel_loudness
from tripcut_pipeline.render.render_reel import render_reel
from tripcut_pipeline.render.resolve_edge_fades import resolve_edge_fades
from tripcut_pipeline.render.smooth_face_track import smooth_face_track
from tripcut_pipeline.render.snap_to_beats import snap_to_beats
from tripcut_pipeline.score.face_box import FaceBox


def render_trip(
    edit_lists: list[dict],
    clips: dict[str, ClipMeta],
    face_boxes: dict[str, list[FaceBox]],
    beat_grids: dict[str, BeatGrid | None],
    audio_mix: AudioMix,
    transition: str,
    loudness_target: float | None,
    intro_outro: str,
    work_dir: Path,
    out_dir: Path,
) -> list[dict]:
    """Stage 5: join touching shots from one clip into one shot, set the joins (--transition), snap cuts to
    the beats of each version's own track, give crossfades their overlap, render cinematic.mp4 / fast.mp4 / story.mp4, then set each reel to
    loudness_target LUFS (None = --loudness off, keep the raw mix). With --intro-outro auto the last shot is held
    longer and each reel fades in from black and out to black with its sound.

    Returns the edit lists as rendered.
    """
    log = logging.getLogger(__name__)
    face_tracks = {clip_id: smooth_face_track(boxes) for clip_id, boxes in face_boxes.items()}
    rendered = []
    for edit_list in edit_lists:
        beat_grid = beat_grids[edit_list["version"]]
        beat_times: list[float] = []
        music_path = None
        if beat_grid is not None:
            beat_times = beat_grid.beat_times
            music_path = beat_grid.path
        snapped = dict(edit_list)
        merged = dict(edit_list)
        merged["shots"] = merge_same_clip_neighbours(edit_list["shots"])
        with_transitions = apply_transition(merged, transition)
        edges = resolve_edge_fades(edit_list["version"], intro_outro)
        clip_durations = {clip_id: clip.duration_s for clip_id, clip in clips.items()}
        held = hold_last_shot(snap_to_beats(with_transitions, beat_times, clips), clip_durations, edges.last_shot_s)
        snapped["shots"] = extend_for_fades(held, clips)
        snapped["intro_outro"] = {
            "video_in_s": edges.video_in_s,
            "audio_in_s": edges.audio_in_s,
            "video_out_s": edges.video_out_s,
            "last_shot_s": edges.last_shot_s,
        }
        out_path = out_dir / f"{edit_list['version']}.mp4"
        try:
            length = render_reel(snapped, clips, face_tracks, music_path, audio_mix, edges, work_dir, out_path)
            if loudness_target is not None:
                snapped["loudness"] = normalize_reel_loudness(out_path, loudness_target, work_dir)
        except CommandError as error:
            raise RenderError(f"{edit_list['version']}: {error}") from error
        snapped["rendered_s"] = round(length, 3)
        log.info("rendered %s (%d shots, %.1f s)", out_path.name, len(snapped["shots"]), length)
        rendered.append(snapped)
    return rendered
