"""Model names and download URLs (all CPU models, cached under ~/.cache/tripcut)."""

SIGLIP_MODEL_NAME = "ViT-B-16-SigLIP"
SIGLIP_PRETRAINED = "webli"
FACE_MODEL_FILE = "blaze_face_short_range.tflite"
FACE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_detector/"
    "blaze_face_short_range/float16/latest/blaze_face_short_range.tflite"
)
AUDIO_MODEL_FILE = "yamnet.tflite"
AUDIO_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/audio_classifier/yamnet/float32/latest/yamnet.tflite"
)
