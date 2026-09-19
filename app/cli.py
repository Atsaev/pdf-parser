from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from app.config import configure_logging
from app.infrastructure.pdf_reader import PdfAssemblyReader, PdfTicketReader
from app.infrastructure.pdf_writer import PdfPageWriter
from app.services.filter_service import FilterService

log = logging.getLogger("app.cli")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Оставляет в ticket-PDF страницы, чьи номера отправления есть в листе сборки."
    )
    parser.add_argument("-a", "--assembly", type=Path, required=True, help="PDF листа сборки")
    parser.add_argument("-t", "--ticket", type=Path, required=True, help="PDF с этикетками")
    parser.add_argument("-o", "--output", type=Path, default=Path("filtered_ticket.pdf"))
    parser.add_argument("-v", "--verbose", action="store_true", help="подробный лог")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    configure_logging()
    logging.getLogger("app").setLevel(logging.DEBUG if args.verbose else logging.INFO)

    service = FilterService(PdfAssemblyReader(), PdfTicketReader(), PdfPageWriter())
    report = service.filter(args.assembly, args.ticket, args.output)
    if report.assembly_total == 0:
        log.error("В листе сборки не найдено ни одного номера отправления")
        return 1
    if not report.has_matches:
        log.error("Совпадений нет, файл %s не создан", args.output)
        return 2
    log.info("Совпадений: %d из %d", report.matched_pages, report.ticket_pages)
    log.info("Записано страниц: %d → %s", report.matched_pages, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
