from tripcut_pipeline.config.director_constants import VERSION_SHOT_COUNTS
from tripcut_pipeline.direct.describe_segment import describe_segment
from tripcut_pipeline.direct.director_request import DirectorRequest
from tripcut_pipeline.direct.encode_keyframe import encode_keyframe


def build_director_content(request: DirectorRequest) -> list[dict]:
    """User message content: trip summary, then 'text line + keyframe image' for each segment."""
    places = sorted({clip.location for clip in request.clips.values() if clip.location is not None})
    place_text = "no GPS in the clips"
    if len(places) > 0:
        place_text = ", ".join(places[:5])
    counts = ", ".join(f"{version} about {count} shots" for version, count in VERSION_SHOT_COUNTS.items())
    intro = (
        f"Trip folder: {request.trip_name}\n"
        f"Clips: {len(request.clips)}. GPS (ISO 6709): {place_text}\n"
        f"Each reel is about {request.duration_s} seconds. Shots per version: {counts}.\n"
        f"Candidate segments ({len(request.segments)}), in filming order:"
    )
    content: list[dict] = [{"type": "text", "text": intro}]
    for segment in request.segments:
        clip = request.clips[segment.clip_id]
        content.append({"type": "text", "text": describe_segment(segment, clip)})
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": encode_keyframe(segment.keyframe_path),
                },
            }
        )
    content.append({"type": "text", "text": "Now return the title and the three edit lists."})
    return content
