def read_first_tag(tags: dict, keys: tuple[str, ...]) -> str | None:
    """Return the first tag value found under any of the keys, or None."""
    for key in keys:
        if key in tags:
            value = str(tags[key]).strip()
            if value != "":
                return value
    return None
