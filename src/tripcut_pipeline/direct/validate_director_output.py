from tripcut_pipeline.config.director_constants import VERSIONS
from tripcut_pipeline.errors.director_error import DirectorError


def validate_director_output(output: dict, known_ids: set[str]) -> dict[str, list[dict]]:
    """Check the parsed answer: all three versions, known ids, no repeats. Returns shots per version."""
    if not isinstance(output, dict) or "edit_lists" not in output:
        raise DirectorError("answer has no edit_lists")
    by_version: dict[str, list[dict]] = {}
    for edit_list in output["edit_lists"]:
        version = edit_list.get("version")
        if version not in VERSIONS:
            raise DirectorError(f"unknown version {version!r}")
        if version in by_version:
            raise DirectorError(f"version {version} appears twice")
        seen: set[str] = set()
        shots = []
        for shot in edit_list.get("shots", []):
            segment_id = shot.get("segment_id")
            if segment_id not in known_ids:
                raise DirectorError(f"{version}: unknown segment {segment_id!r}")
            if segment_id in seen:
                continue
            seen.add(segment_id)
            shots.append({"segment_id": segment_id, "crop": shot.get("crop", "center")})
        if len(shots) == 0:
            raise DirectorError(f"{version}: no shots")
        by_version[version] = shots
    for version in VERSIONS:
        if version not in by_version:
            raise DirectorError(f"missing version {version}")
    return by_version
