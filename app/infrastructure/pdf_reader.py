from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pdfplumber

from app.domain.assembly import AssemblyList
from app.domain.label import LabelCode, TicketCode
from app.domain.shipment import SHIPMENT_SEARCH_RE, ShipmentNumber

TAIL_RE = re.compile(r"^-\d{4}-\d{1,2}$")
PREFIX_PART_RE = re.compile(r"^\d{4,6}$")
LABEL_RE = re.compile(r"^ii\d+$")
DIGITS_RE = re.compile(r"^\d+$")

COLUMN_TOLERANCE = 0.2
SAME_LINE_TOLERANCE = 6.0

Word = dict[str, Any]


def extract_assembly_numbers(words: Iterable[Word]) -> list[ShipmentNumber]:
    """Номера отправлений из колонки «Номер отправления»."""
    numbers: list[ShipmentNumber] = []
    for word in words:
        found = SHIPMENT_SEARCH_RE.match(word["text"])
        number = ShipmentNumber.parse(found.group(0)) if found else None
        if number is not None:
            numbers.append(number)
    return numbers


def extract_assembly_labels(words: Iterable[Word]) -> list[LabelCode]:
    """Идентификаторы из колонки «Номер с этикетки» (есть не во всех листах)."""
    labels: list[LabelCode] = []
    for word in words:
        code = LabelCode.parse(word["text"])
        if code is not None:
            labels.append(code)
    return labels


def extract_ticket_code(words: Iterable[Word], width: float) -> TicketCode | None:
    """Что напечатано на этикетке: идентификатор (новый формат) или номер отправления."""
    words = list(words)
    return _label_code(words) or _shipment_number(words, width)


def _label_code(words: list[Word]) -> LabelCode | None:
    """Новый формат: `ii5009316` и `4196` на одной строке, склеиваются в `ii50093164196`."""
    head = next((word for word in words if LABEL_RE.match(word["text"])), None)
    if head is None:
        return None
    rest = [
        word
        for word in words
        if word is not head
        and DIGITS_RE.match(word["text"])
        and abs(word["top"] - head["top"]) <= SAME_LINE_TOLERANCE
        and word["x0"] > head["x0"]
    ]
    rest.sort(key=lambda word: word["x0"])
    return LabelCode.parse(head["text"] + "".join(word["text"] for word in rest))


def _shipment_number(words: list[Word], width: float) -> ShipmentNumber | None:
    """Старый формат: хвост `-XXXX-X` отдельной колонкой и префикс рядом."""
    tail = next((word for word in words if TAIL_RE.match(word["text"])), None)
    if tail is None:
        return None
    parts = [
        word
        for word in words
        if PREFIX_PART_RE.match(word["text"]) and _near_tail(word, tail, width)
    ]
    parts.sort(key=lambda word: (word["top"], word["x0"]))
    return ShipmentNumber.parse("".join(word["text"] for word in parts) + tail["text"])


def _near_tail(word: Word, tail: Word, width: float) -> bool:
    return abs(word["x0"] - tail["x0"]) <= COLUMN_TOLERANCE * width


class PdfAssemblyReader:
    """Адаптер pdfplumber: читает лист сборки."""

    def read(self, path: Path) -> AssemblyList:
        numbers: list[ShipmentNumber] = []
        labels: list[LabelCode] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                numbers.extend(extract_assembly_numbers(words))
                labels.extend(extract_assembly_labels(words))
        return AssemblyList(tuple(numbers), tuple(labels))


class PdfTicketReader:
    """Адаптер pdfplumber: читает идентификатор с каждой страницы этикетки."""

    def read(self, path: Path) -> list[TicketCode | None]:
        with pdfplumber.open(path) as pdf:
            return [extract_ticket_code(page.extract_words(), page.width) for page in pdf.pages]
