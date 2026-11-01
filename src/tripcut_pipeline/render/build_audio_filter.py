from tripcut_pipeline.config.render_constants import AUDIO_LIMIT, MUSIC_FADE_S
from tripcut_pipeline.render.audio_mix import AudioMix


def build_audio_filter(clip_label: str, music_label: str | None, audio_mix: AudioMix, fade_start: float) -> str:
    """ffmpeg -filter_complex part for the reel's sound, output label [a].

    clip_label is the joined clip sound ("[0:a]" after the concat demuxer, "[ca]" after the crossfade chain),
    music_label the looped music track input, or None for no music.
    With music: clip sound at clip_volume + music at music_volume, limited so the sum does not clip.
    Without music: clip sound at full level. Both fade out at the end.
    """
    fade = f"afade=t=out:st={fade_start:.3f}:d={MUSIC_FADE_S}"
    if music_label is None:
        return f"{clip_label}{fade}[a]"
    return (
        f"{clip_label}volume={audio_mix.clip_volume:.3f}[clip];"
        f"{music_label}volume={audio_mix.music_volume:.3f}[music];"
        f"[clip][music]amix=inputs=2:duration=first:normalize=0,"
        f"alimiter=limit={AUDIO_LIMIT},{fade}[a]"
    )
