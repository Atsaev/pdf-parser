from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.domain.report import FilterReport
from app.domain.shipment import ShipmentNumber
from app.services.ports import AssemblyReader, PageWriter, TicketReader

log = logging.getLogger("app.filter")


@dataclass(frozen=True, slots=True)
class FilterService:
    """Оставляет в ticket только страницы, чьи номера есть в листе сборки."""

    assembly_reader: AssemblyReader
    ticket_reader: TicketReader
    writer: PageWriter

    def filter(self, assembly: Path, ticket: Path, output: Path) -> FilterReport:
        wanted = {number.key for number in self.assembly_reader.read(assembly)}
        numbers = self.ticket_reader.read(ticket)
        hits = self._select(numbers, wanted)
        if hits:
            self.writer.write(ticket, [index for index, _ in hits], output)
        log.info("%s: совпадений %d из %d", ticket.name, len(hits), len(numbers))
        return FilterReport(
            assembly_total=len(wanted),
            ticket_name=ticket.name,
            ticket_pages=len(numbers),
            matched=tuple(number for _, number in hits),
            output=output if hits else None,
        )

    @staticmethod
    def _select(numbers: list[ShipmentNumber | None], wanted: set[str]) -> list[tuple[int, ShipmentNumber]]:
        hits: list[tuple[int, ShipmentNumber]] = []
        for index, number in enumerate(numbers):
            if number is not None and number.key in wanted:
                hits.append((index, number))
        return hits
