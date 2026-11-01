import re

from tripcut_pipeline.ingest.clip_meta import ClipMeta


def clip_name_sort_key(meta: ClipMeta) -> list[tuple[int, int, str]]:
    """Natural file-name order (IMG_9 before IMG_10, case ignored): the CLI's "upload" order."""
    key = []
    for part in re.split(r"(\d+)", str(meta.path).lower()):
        if part == "":
            continue
        if part.isdigit():
            key.append((0, int(part), part))
        else:
            key.append((1, 0, part))
    return key
