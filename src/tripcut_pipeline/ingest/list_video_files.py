from pathlib import Path

from tripcut_pipeline.config.ingest_constants import VIDEO_EXTENSIONS


def list_video_files(trip_dir: Path) -> list[Path]:
    """All .mov/.mp4/.m4v files under the trip folder (recursive), hidden files skipped."""
    files = []
    for path in sorted(trip_dir.rglob("*")):
        if path.name.startswith("."):
            continue
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
            files.append(path)
    return files
