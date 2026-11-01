from pathlib import Path

import librosa
import numpy as np
from mediapipe.tasks.python import audio
from mediapipe.tasks.python.components.containers.audio_data import AudioData
from mediapipe.tasks.python.core.base_options import BaseOptions

from tripcut_pipeline.config.ingest_constants import AUDIO_SAMPLE_RATE
from tripcut_pipeline.config.model_constants import AUDIO_MODEL_FILE, AUDIO_MODEL_URL
from tripcut_pipeline.score.audio_event_constants import AUDIO_EVENT_GROUPS, AUDIO_SCORE_THRESHOLD
from tripcut_pipeline.tools.download_model_file import download_model_file


class AudioEventClassifierService:
    """YAMNet through MediaPipe Audio Classifier: per ~1 s window, a 0-1 score per event group."""

    def __init__(self) -> None:
        model_path = download_model_file(AUDIO_MODEL_URL, AUDIO_MODEL_FILE)
        options = audio.AudioClassifierOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            score_threshold=AUDIO_SCORE_THRESHOLD,
        )
        self._classifier = audio.AudioClassifier.create_from_options(options)

    def classify_file(self, wav_path: Path) -> list[tuple[float, dict[str, float]]]:
        samples, sample_rate = librosa.load(str(wav_path), sr=AUDIO_SAMPLE_RATE, mono=True)
        if len(samples) == 0:
            return []
        clip = AudioData.create_from_array(samples.astype(np.float32), float(sample_rate))
        windows = []
        for result in self._classifier.classify(clip):
            groups = {name: 0.0 for name in AUDIO_EVENT_GROUPS}
            if len(result.classifications) > 0:
                for category in result.classifications[0].categories:
                    for group, labels in AUDIO_EVENT_GROUPS.items():
                        if category.category_name in labels:
                            groups[group] = max(groups[group], float(category.score))
            time_s = 0.0
            if result.timestamp_ms is not None:
                time_s = result.timestamp_ms / 1000.0
            windows.append((time_s, groups))
        return windows

    def close(self) -> None:
        self._classifier.close()
