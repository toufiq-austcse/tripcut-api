import hashlib
import json
from pathlib import Path

import librosa
import numpy as np

from tripcut_pipeline.config.paths_constants import BEAT_CACHE_DIR
from tripcut_pipeline.music.beat_grid import BeatGrid
from tripcut_pipeline.tools.run_command import run_command
from tripcut_pipeline.tools.write_json import write_json


def load_beat_grid(track_path: Path) -> BeatGrid:
    """Beat times for a track, cached by file hash.

    ffmpeg decodes any format to wav, librosa tracks the beats, and the grid is extended back to 0 s
    at the tempo because the tracker drops weak intro beats.
    """
    digest = hashlib.sha1(track_path.read_bytes()).hexdigest()
    cache_path = BEAT_CACHE_DIR / f"{digest}.json"
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        BEAT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        wav_path = BEAT_CACHE_DIR / f"{digest}.wav"
        run_command(["ffmpeg", "-y", "-v", "error", "-i", str(track_path), "-ac", "1", "-ar", "22050", str(wav_path)])
        samples, sample_rate = librosa.load(str(wav_path), sr=22050, mono=True)
        wav_path.unlink()
        tempo, beat_times = librosa.beat.beat_track(y=samples, sr=sample_rate, units="time")
        tempo_bpm = float(np.atleast_1d(tempo)[0])
        beats = [float(time_s) for time_s in beat_times]
        if len(beats) > 0 and tempo_bpm > 0:
            interval = 60.0 / tempo_bpm
            while beats[0] - interval >= 0.0:
                beats.insert(0, beats[0] - interval)
        cached = {
            "tempo_bpm": round(tempo_bpm, 2),
            "duration_s": round(len(samples) / sample_rate, 3),
            "beat_times": [round(time_s, 3) for time_s in beats],
        }
        write_json(cache_path, cached)
    return BeatGrid(
        music_id=track_path.stem,
        path=track_path,
        tempo_bpm=float(cached["tempo_bpm"]),
        duration_s=float(cached["duration_s"]),
        beat_times=[float(time_s) for time_s in cached["beat_times"]],
    )
