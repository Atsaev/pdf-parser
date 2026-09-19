from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pypdf import PdfReader, PdfWriter


class PdfPageWriter:
    """Собирает новый PDF из выбранных страниц исходного файла."""

    def write(self, source: Path, indices: Iterable[int], output: Path) -> None:
        reader = PdfReader(source)
        writer = PdfWriter()
        for index in indices:
            writer.add_page(reader.pages[index])
        with output.open("wb") as stream:
            writer.write(stream)
