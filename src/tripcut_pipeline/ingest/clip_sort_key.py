from datetime import datetime

from tripcut_pipeline.config.order_constants import NO_TIME_SORT_VALUE
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.ingest.parse_creation_time import parse_creation_time


def clip_sort_key(meta: ClipMeta) -> tuple[int, datetime, str]:
    """Order clips by real capture time (UTC), then by file name; clips with no time go last."""
    captured = parse_creation_time(meta.creation_time)
    if captured is None:
        return (1, NO_TIME_SORT_VALUE, meta.path.name)
    return (0, captured, meta.path.name)
