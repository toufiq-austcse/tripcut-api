from tripcut_pipeline.config.director_constants import VERSIONS
from tripcut_pipeline.direct.build_edit_list import build_edit_list
from tripcut_pipeline.direct.director_request import DirectorRequest


def build_edit_lists(request: DirectorRequest, title: str, shots_by_version: dict[str, list[dict]]) -> list[dict]:
    """Build the three contract edit lists in the fixed order cinematic, fast, story."""
    segments_by_id = {segment.segment_id: segment for segment in request.segments}
    edit_lists = []
    for version in VERSIONS:
        edit_lists.append(
            build_edit_list(
                version, title, shots_by_version[version], segments_by_id, request.duration_s, request.music_ids[version],
                request.order,
            )
        )
    return edit_lists
