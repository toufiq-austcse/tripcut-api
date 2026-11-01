from pathlib import Path

from tripcut_pipeline.config.render_constants import AUDIO_BITRATE, MUSIC_FADE_S
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.render.audio_mix import AudioMix
from tripcut_pipeline.render.build_audio_filter import build_audio_filter
from tripcut_pipeline.render.plan_face_crop import plan_face_crop
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
    """Render every shot, join them with the concat demuxer, mix the music with the clip sound. Returns length in s."""
    shot_dir = work_dir / f"shots_{edit_list['version']}"
    shot_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    total = 0.0
    for index, shot in enumerate(edit_list["shots"]):
        clip = clips[shot["clip_id"]]
        track = []
        if shot["clip_id"] in face_tracks:
            track = face_tracks[shot["clip_id"]]
        shot_path = shot_dir / f"{index:03d}.mp4"
        render_shot(clip, shot, plan_face_crop(clip, shot, track), shot_path)
        lines.append(f"file '{shot_path.resolve()}'")
        total += float(shot["out"]) - float(shot["in"])
    list_path = shot_dir / "concat.txt"
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    fade_start = max(0.0, total - MUSIC_FADE_S)
    args = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(list_path)]
    if music_path is not None:
        args += ["-stream_loop", "-1", "-i", str(music_path)]
    audio_filter = build_audio_filter(music_path is not None, audio_mix, fade_start)
    args += [
        "-map", "0:v:0", "-filter_complex", audio_filter, "-map", "[a]", "-c:v", "copy",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-t", f"{total:.3f}", "-movflags", "+faststart", str(out_path),
    ]
    run_command(args)
    return total
