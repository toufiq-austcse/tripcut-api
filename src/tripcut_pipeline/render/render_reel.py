from pathlib import Path

from tripcut_pipeline.config.render_constants import (
    AUDIO_BITRATE,
    MUSIC_FADE_S,
    OUTPUT_FPS,
    VIDEO_CRF,
    VIDEO_PRESET,
)
from tripcut_pipeline.config.transition_constants import TRANSITION_FADE
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.render.audio_mix import AudioMix
from tripcut_pipeline.render.build_audio_filter import build_audio_filter
from tripcut_pipeline.render.build_transition_filter import build_transition_filter
from tripcut_pipeline.render.plan_face_crop import plan_face_crop
from tripcut_pipeline.render.plan_shot_frames import plan_shot_frames
from tripcut_pipeline.render.render_shot import render_shot
from tripcut_pipeline.tools.run_command import run_command


def render_reel(
    edit_list: dict,
    clips: dict[str, ClipMeta],
    face_tracks: dict[str, list[tuple[float, float]]],
    music_path: Path | None,
    audio_mix: AudioMix,
    work_dir: Path,
    out_path: Path,
) -> float:
    """Render every shot as an exact number of frames, join them, mix the music with the clip sound.

    Only cuts: concat demuxer with -c:v copy (no second video encode). Any crossfade: one ffmpeg pass with
    xfade + acrossfade (build_transition_filter), which encodes the reel video again. Returns length in s.
    """
    shot_dir = work_dir / f"shots_{edit_list['version']}"
    shot_dir.mkdir(parents=True, exist_ok=True)
    shots = edit_list["shots"]
    frame_counts = plan_shot_frames(shots)
    shot_paths = []
    has_fade = False
    total_frames = 0
    for index, shot in enumerate(shots):
        clip = clips[shot["clip_id"]]
        track = []
        if shot["clip_id"] in face_tracks:
            track = face_tracks[shot["clip_id"]]
        shot_path = shot_dir / f"{index:03d}.mov"
        render_shot(clip, shot, frame_counts[index], plan_face_crop(clip, shot, track), shot_path)
        shot_paths.append(shot_path)
        total_frames += frame_counts[index]
        if shot["transition"] == TRANSITION_FADE:
            has_fade = True
            total_frames -= round(float(shot["transition_s"]) * OUTPUT_FPS)
    total = total_frames / OUTPUT_FPS
    fade_start = max(0.0, total - MUSIC_FADE_S)

    music_label = None
    if has_fade:
        args = ["ffmpeg", "-y", "-v", "error"]
        for shot_path in shot_paths:
            args += ["-i", str(shot_path)]
        if music_path is not None:
            args += ["-stream_loop", "-1", "-i", str(music_path)]
            music_label = f"[{len(shot_paths)}:a]"
        audio_filter = build_audio_filter("[ca]", music_label, audio_mix, fade_start)
        video_args = [
            "-filter_complex", build_transition_filter(shots, frame_counts) + ";" + audio_filter,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", VIDEO_PRESET, "-crf", str(VIDEO_CRF), "-pix_fmt", "yuv420p",
        ]
    else:
        lines = [f"file '{shot_path.resolve()}'" for shot_path in shot_paths]
        list_path = shot_dir / "concat.txt"
        list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        args = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(list_path)]
        if music_path is not None:
            args += ["-stream_loop", "-1", "-i", str(music_path)]
            music_label = "[1:a]"
        audio_filter = build_audio_filter("[0:a]", music_label, audio_mix, fade_start)
        video_args = ["-map", "0:v:0", "-filter_complex", audio_filter, "-map", "[a]", "-c:v", "copy"]
    args += video_args
    args += ["-c:a", "aac", "-b:a", AUDIO_BITRATE, "-t", f"{total:.6f}", "-movflags", "+faststart", str(out_path)]
    run_command(args)
    return total
