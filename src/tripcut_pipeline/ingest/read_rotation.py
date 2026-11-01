def read_rotation(stream: dict) -> int:
    """Rotation in degrees from the display matrix side data or the legacy 'rotate' tag."""
    side_data = stream.get("side_data_list", [])
    for item in side_data:
        if "rotation" in item:
            return int(float(item["rotation"])) % 360
    tags = stream.get("tags", {})
    if "rotate" in tags:
        return int(float(tags["rotate"])) % 360
    return 0
