"""Порты (границы) приложения: сервис зависит от интерфейсов, а не от PDF-библиотек."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from app.domain.assembly import AssemblyList
from app.domain.label import TicketCode
from app.domain.report import FilterReport


class AssemblyReader(Protocol):
    def read(self, path: Path) -> AssemblyList: ...


class TicketReader(Protocol):
    def read(self, path: Path) -> list[TicketCode | None]: ...


class PageWriter(Protocol):
    def write(self, source: Path, indices: Iterable[int], output: Path) -> None: ...


class FilterRunner(Protocol):
    def filter(self, assembly: Path, ticket: Path, output: Path) -> FilterReport: ...
