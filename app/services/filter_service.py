from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from app.domain.label import TicketCode
from app.domain.report import FilterReport
from app.services.ports import AssemblyReader, PageWriter, TicketReader

log = logging.getLogger("app.filter")


@dataclass(frozen=True, slots=True)
class FilterService:
    """Оставляет в ticket только страницы, которые есть в листе сборки."""

    assembly_reader: AssemblyReader
    ticket_reader: TicketReader
    writer: PageWriter

    def filter(self, assembly: Path, ticket: Path, output: Path) -> FilterReport:
        listing = self.assembly_reader.read(assembly)
        wanted = listing.keys
        codes = self.ticket_reader.read(ticket)
        hits = self._select(codes, wanted)
        if hits:
            self.writer.write(ticket, [index for index, _ in hits], output)
        log.info("%s: совпадений %d из %d", ticket.name, len(hits), len(codes))
        return FilterReport(
            assembly_numbers=len(listing.numbers),
            assembly_labels=len(listing.labels),
            ticket_name=ticket.name,
            ticket_pages=len(codes),
            matched=tuple(code for _, code in hits),
            output=output if hits else None,
        )

    @staticmethod
    def _select(codes: list[TicketCode | None], wanted: frozenset[str]) -> list[tuple[int, TicketCode]]:
        hits: list[tuple[int, TicketCode]] = []
        for index, code in enumerate(codes):
            if code is not None and code.key in wanted:
                hits.append((index, code))
        return hits
