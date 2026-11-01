from pathlib import Path

import numpy as np
import open_clip
import torch
import torch.nn.functional as functional
from PIL import Image

from tripcut_pipeline.config.model_constants import SIGLIP_MODEL_NAME, SIGLIP_PRETRAINED
from tripcut_pipeline.config.paths_constants import MODEL_DIR
from tripcut_pipeline.config.score_constants import SIGLIP_BATCH_SIZE
from tripcut_pipeline.score.siglip_prompts_constants import NEGATIVE_PROMPTS, POSITIVE_PROMPTS


class SiglipScorerService:
    """SigLIP ViT-B/16 on CPU: one image embedding per keyframe plus a 0-1 'good travel moment' score."""

    def __init__(self) -> None:
        model, _, preprocess = open_clip.create_model_and_transforms(
            SIGLIP_MODEL_NAME, pretrained=SIGLIP_PRETRAINED, cache_dir=str(MODEL_DIR / "open_clip")
        )
        model.eval()
        self._model = model
        self._preprocess = preprocess
        tokenizer = open_clip.get_tokenizer(SIGLIP_MODEL_NAME)
        prompts = list(POSITIVE_PROMPTS) + list(NEGATIVE_PROMPTS)
        with torch.no_grad():
            text_features = model.encode_text(tokenizer(prompts))
        self._text_features = functional.normalize(text_features, dim=-1)
        self._positive_count = len(POSITIVE_PROMPTS)

    def score_images(self, paths: list[Path]) -> list[tuple[np.ndarray, float]]:
        results: list[tuple[np.ndarray, float]] = []
        for offset in range(0, len(paths), SIGLIP_BATCH_SIZE):
            batch_paths = paths[offset:offset + SIGLIP_BATCH_SIZE]
            images = torch.stack([self._preprocess(Image.open(path).convert("RGB")) for path in batch_paths])
            with torch.no_grad():
                image_features = functional.normalize(self._model.encode_image(images), dim=-1)
                logits = image_features @ self._text_features.T * self._model.logit_scale.exp()
                probabilities = logits.softmax(dim=-1)
            positive = probabilities[:, :self._positive_count].sum(dim=-1)
            for index in range(len(batch_paths)):
                results.append((image_features[index].numpy().copy(), float(positive[index])))
        return results
