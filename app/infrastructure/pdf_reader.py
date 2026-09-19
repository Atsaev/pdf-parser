from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pdfplumber

from app.domain.shipment import SHIPMENT_SEARCH_RE, ShipmentNumber

TAIL_RE = re.compile(r"^-\d{4}-\d$")
PREFIX_PART_RE = re.compile(r"^\d{4,6}$")
COLUMN_TOLERANCE = 0.2

Word = dict[str, Any]


def extract_assembly_numbers(words: Iterable[Word]) -> list[ShipmentNumber]:
    """Достаёт номера отправлений из слов страницы листа сборки."""
    numbers: list[ShipmentNumber] = []
    for word in words:
        found = SHIPMENT_SEARCH_RE.match(word["text"])
        number = ShipmentNumber.parse(found.group(0)) if found else None
        if number is not None:
            numbers.append(number)
    return numbers


def reconstruct_ticket_number(words: Iterable[Word], width: float) -> ShipmentNumber | None:
    """Собирает номер со страницы этикетки: префикс из соседних колонок + хвост."""
    words = list(words)
    tail = next((word for word in words if TAIL_RE.match(word["text"])), None)
    if tail is None:
        return None
    parts = [word for word in words if PREFIX_PART_RE.match(word["text"]) and _near_tail(word, tail, width)]
    parts.sort(key=lambda word: (word["top"], word["x0"]))
    return ShipmentNumber.parse("".join(word["text"] for word in parts) + tail["text"])


def _near_tail(word: Word, tail: Word, width: float) -> bool:
    return abs(word["x0"] - tail["x0"]) <= COLUMN_TOLERANCE * width


class PdfAssemblyReader:
    """Адаптер pdfplumber: читает номера из листа сборки."""

    def read(self, path: Path) -> list[ShipmentNumber]:
        numbers: list[ShipmentNumber] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                numbers.extend(extract_assembly_numbers(page.extract_words()))
        return numbers


class PdfTicketReader:
    """Адаптер pdfplumber: восстанавливает номер с каждой страницы этикетки.

    Текст этикетки повёрнут: хвост `-XXXX-X` идёт отдельной колонкой, а префикс —
    одной-двумя группами цифр в соседней колонке рядом с хвостом.
    """

    def read(self, path: Path) -> list[ShipmentNumber | None]:
        with pdfplumber.open(path) as pdf:
            return [reconstruct_ticket_number(page.extract_words(), page.width) for page in pdf.pages]
