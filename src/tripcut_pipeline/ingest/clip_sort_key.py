from tripcut_pipeline.ingest.clip_meta import ClipMeta


def clip_sort_key(meta: ClipMeta) -> tuple[str, str]:
    """Order clips by creation time when known, then by file name."""
    creation = ""
    if meta.creation_time is not None:
        creation = meta.creation_time
    return (creation, meta.path.name)
