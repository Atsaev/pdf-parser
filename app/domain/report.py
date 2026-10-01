from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.domain.label import TicketCode


@dataclass(frozen=True, slots=True)
class FilterReport:
    """Результат фильтрации одной этикетки по листу сборки."""

    assembly_numbers: int
    assembly_labels: int
    ticket_name: str
    ticket_pages: int
    matched: tuple[TicketCode, ...]
    output: Path | None

    @property
    def has_assembly(self) -> bool:
        return self.assembly_numbers + self.assembly_labels > 0

    @property
    def matched_pages(self) -> int:
        return len(self.matched)

    @property
    def has_matches(self) -> bool:
        return bool(self.matched)
