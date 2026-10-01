from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.shipment import ShipmentNumber

FULL_LABEL_RE = re.compile(r"^ii\d{1,17}$")


@dataclass(frozen=True, slots=True)
class LabelCode:
    """Идентификатор этикетки нового формата, например `ii50093164196`."""

    value: str

    @classmethod
    def parse(cls, raw: str) -> LabelCode | None:
        return cls(raw) if FULL_LABEL_RE.match(raw) else None

    @property
    def key(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value


TicketCode = ShipmentNumber | LabelCode
"""То, что может быть напечатано на этикетке: номер отправления или её идентификатор."""
