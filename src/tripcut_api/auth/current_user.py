from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CurrentUser:
    """The signed-in Supabase user taken from a verified access token."""

    id: UUID
    email: str | None
