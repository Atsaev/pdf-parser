from __future__ import annotations

from dataclasses import dataclass

from app.domain.label import LabelCode
from app.domain.shipment import ShipmentNumber


@dataclass(frozen=True, slots=True)
class AssemblyList:
    """Лист сборки: номера отправлений и идентификаторы этикеток (новый формат)."""

    numbers: tuple[ShipmentNumber, ...]
    labels: tuple[LabelCode, ...]

    @property
    def keys(self) -> frozenset[str]:
        numbers = {number.key for number in self.numbers}
        return frozenset(numbers | {label.key for label in self.labels})
