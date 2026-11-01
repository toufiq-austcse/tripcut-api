from tripcut_pipeline.config.director_constants import VERSION_SHOT_COUNTS, VERSIONS
from tripcut_pipeline.direct.build_edit_lists import build_edit_lists
from tripcut_pipeline.direct.director_request import DirectorRequest
from tripcut_pipeline.direct.director_result import DirectorResult


class FallbackDirectorService:
    """No-LLM director (TDD-001 §8.3 fallback): top-scored segments per version, in filming order."""

    def direct(self, request: DirectorRequest) -> DirectorResult:
        by_score = sorted(request.segments, key=lambda segment: segment.score, reverse=True)
        shots_by_version: dict[str, list[dict]] = {}
        for version in VERSIONS:
            chosen = by_score[:VERSION_SHOT_COUNTS[version]]
            chosen = sorted(chosen, key=lambda segment: segment.segment_id)
            shots = []
            for segment in chosen:
                crop = "center"
                if len(segment.face_boxes) > 0:
                    crop = "face"
                shots.append({"segment_id": segment.segment_id, "crop": crop})
            shots_by_version[version] = shots
        return DirectorResult(
            edit_lists=build_edit_lists(request, request.trip_name, shots_by_version),
            director="fallback",
            model=None,
        )
