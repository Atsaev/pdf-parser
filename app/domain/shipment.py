from __future__ import annotations

import re
from dataclasses import dataclass

SHIPMENT_SEARCH_RE = re.compile(r"\d{8,12}-\d{4}-\d")
FULL_RE = re.compile(r"^\d{8,12}-\d{4}-\d$")


@dataclass(frozen=True, slots=True)
class ShipmentNumber:
    """Номер отправления вида `<префикс>-<4 цифры>-<1 цифра>`."""

    prefix: str
    middle: str
    tail: str

    @classmethod
    def parse(cls, raw: str) -> ShipmentNumber | None:
        if not FULL_RE.match(raw):
            return None
        prefix, middle, tail = raw.split("-")
        return cls(prefix, middle, tail)

    @property
    def key(self) -> str:
        """Канонический вид для сравнения: без ведущих нулей в префиксе."""
        return f"{self.prefix.lstrip('0') or '0'}-{self.middle}-{self.tail}"

    def __str__(self) -> str:
        return f"{self.prefix}-{self.middle}-{self.tail}"
