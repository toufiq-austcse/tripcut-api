import dataclasses
import logging
from pathlib import Path

from tripcut_pipeline.config.order_constants import ORDER_UPLOAD
from tripcut_pipeline.errors.bad_input_error import BadInputError
from tripcut_pipeline.errors.command_error import CommandError
from tripcut_pipeline.ingest.clip_meta import ClipMeta
from tripcut_pipeline.ingest.clip_name_sort_key import clip_name_sort_key
from tripcut_pipeline.ingest.clip_proxy import ClipProxy
from tripcut_pipeline.ingest.clip_sort_key import clip_sort_key
from tripcut_pipeline.ingest.list_video_files import list_video_files
from tripcut_pipeline.ingest.make_proxy import make_proxy
from tripcut_pipeline.ingest.probe_clip import probe_clip


def ingest_trip(trip_dir: Path, work_dir: Path, order: str) -> list[ClipProxy]:
    """Stage 1: probe every clip, sort them (upload = file-name order, else capture time), one proxy per clip.

    Clip ids c01, c02, ... follow that order, so later stages can sort by them.
    """
    log = logging.getLogger(__name__)
    if not trip_dir.is_dir():
        raise BadInputError(f"{trip_dir} is not a folder")
    files = list_video_files(trip_dir)
    if len(files) == 0:
        raise BadInputError(f"{trip_dir} has no .mov/.mp4/.m4v clips")

    metas: list[ClipMeta] = []
    for path in files:
        try:
            metas.append(probe_clip(path, "tmp"))
        except (CommandError, ValueError, KeyError) as error:
            log.warning("skipping unreadable clip %s: %s", path.name, error)
    if len(metas) == 0:
        raise BadInputError(f"{trip_dir}: no readable clips")

    if order == ORDER_UPLOAD:
        metas.sort(key=clip_name_sort_key)
    else:
        metas.sort(key=clip_sort_key)
    proxies: list[ClipProxy] = []
    for index, meta in enumerate(metas, start=1):
        clip_id = f"c{index:02d}"
        numbered = dataclasses.replace(meta, clip_id=clip_id)
        log.info("ingest %s %s (%.1f s, %dx%d %s)", clip_id, meta.path.name, meta.duration_s,
                 meta.width, meta.height, meta.codec)
        proxies.append(make_proxy(numbered, work_dir))
    return proxies
