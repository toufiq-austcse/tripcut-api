from tripcut_pipeline.config.render_constants import AUDIO_LIMIT, MUSIC_FADE_S
from tripcut_pipeline.render.audio_mix import AudioMix


def build_audio_filter(has_music: bool, audio_mix: AudioMix, fade_start: float) -> str:
    """ffmpeg -filter_complex for the reel's sound, output label [a].

    Input 0 is the joined shots (clip sound), input 1 the looped music track.
    With music: clip sound at clip_volume + music at music_volume, limited so the sum does not clip.
    Without music: clip sound at full level. Both fade out at the end.
    """
    fade = f"afade=t=out:st={fade_start:.3f}:d={MUSIC_FADE_S}"
    if not has_music:
        return f"[0:a]{fade}[a]"
    return (
        f"[0:a]volume={audio_mix.clip_volume:.3f}[clip];"
        f"[1:a]volume={audio_mix.music_volume:.3f}[music];"
        f"[clip][music]amix=inputs=2:duration=first:normalize=0,"
        f"alimiter=limit={AUDIO_LIMIT},{fade}[a]"
    )
