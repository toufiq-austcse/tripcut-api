from dataclasses import dataclass, field


@dataclass(frozen=True)
class DirectorResult:
    """Three edit lists (TDD-001 §8.4 contract) plus what the call cost."""

    edit_lists: list[dict]
    director: str
    model: str | None
    tokens_in: int = 0
    tokens_out: int = 0
    attempts: int = 0
    fallback: bool = False
    fallback_reason: str | None = None
    notes: list[str] = field(default_factory=list)
