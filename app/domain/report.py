from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.domain.shipment import ShipmentNumber


@dataclass(frozen=True, slots=True)
class FilterReport:
    """Результат фильтрации одной этикетки по листу сборки."""

    assembly_total: int
    ticket_name: str
    ticket_pages: int
    matched: tuple[ShipmentNumber, ...]
    output: Path | None

    @property
    def matched_pages(self) -> int:
        return len(self.matched)

    @property
    def has_matches(self) -> bool:
        return bool(self.matched)
