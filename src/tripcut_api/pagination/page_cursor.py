from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class PageCursor:
    """Keyset position: the (created_at, id) of the last row on the previous page."""

    created_at: datetime
    id: UUID
