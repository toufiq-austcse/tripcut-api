from datetime import datetime, timezone


def parse_creation_time(raw: str | None) -> datetime | None:
    """ffprobe creation time ("2026-10-15T14:19:03+0100", "...000000Z") -> UTC datetime, or None.

    A time with no offset is read as UTC. An empty or unreadable value gives None.
    """
    if raw is None:
        return None
    text = raw.strip()
    if text == "":
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
