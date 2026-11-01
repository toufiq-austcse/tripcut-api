import logging

import cv2

from tripcut_pipeline.ingest.clip_proxy import ClipProxy
from tripcut_pipeline.score.aggregate_audio_events import aggregate_audio_events
from tripcut_pipeline.score.audio_event_classifier_service import AudioEventClassifierService
from tripcut_pipeline.score.build_segments import build_segments
from tripcut_pipeline.score.face_box import FaceBox
from tripcut_pipeline.score.face_detector_service import FaceDetectorService
from tripcut_pipeline.score.measure_faces import measure_faces
from tripcut_pipeline.score.measure_quality import measure_quality
from tripcut_pipeline.score.measure_shake import measure_shake
from tripcut_pipeline.score.rank_segments import rank_segments
from tripcut_pipeline.score.score_result import ScoreResult
from tripcut_pipeline.score.segment import Segment
from tripcut_pipeline.score.siglip_scorer_service import SiglipScorerService


def score_trip(proxies: list[ClipProxy]) -> ScoreResult:
    """Stage 2: segments per clip, quality/shake/faces/audio/SigLIP features, then rank to the top 60."""
    log = logging.getLogger(__name__)
    faces = FaceDetectorService()
    audio = AudioEventClassifierService()
    siglip = SiglipScorerService()
    segments: list[Segment] = []
    face_tracks: dict[str, list[FaceBox]] = {}
    try:
        for proxy in proxies:
            clip_segments = build_segments(proxy, len(segments) + 1)
            windows = []
            if proxy.audio_path is not None:
                windows = audio.classify_file(proxy.audio_path)
            track: list[FaceBox] = []
            for segment in clip_segments:
                image = cv2.imread(str(segment.keyframe_path))
                sharpness, exposure = measure_quality(image)
                boxes: list[FaceBox] = []
                for time_s, frame_path in segment.frames:
                    boxes.extend(faces.detect(frame_path, time_s))
                face_count, face_size = measure_faces(boxes)
                segment.face_boxes = boxes
                track.extend(boxes)
                segment.features = {
                    "sharpness": round(sharpness, 3),
                    "exposure": round(exposure, 3),
                    "stability": round(measure_shake([path for _, path in segment.frames]), 3),
                    "faces": face_count,
                    "face_size": round(face_size, 3),
                }
                for name, value in aggregate_audio_events(windows, segment.start_s, segment.end_s).items():
                    segment.features[name] = round(value, 3)
            face_tracks[proxy.meta.clip_id] = track
            segments.extend(clip_segments)
            log.info("score %s: %d segments", proxy.meta.clip_id, len(clip_segments))

        scored = siglip.score_images([segment.keyframe_path for segment in segments])
        for segment, (embedding, aesthetic) in zip(segments, scored):
            segment.embedding = embedding
            segment.features["aesthetic"] = round(aesthetic, 3)
    finally:
        faces.close()
        audio.close()

    kept = rank_segments(segments)
    return ScoreResult(segment_count=len(segments), kept=kept, face_tracks=face_tracks)
