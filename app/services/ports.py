"""Порты (границы) приложения: сервис зависит от интерфейсов, а не от PDF-библиотек."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from app.domain.report import FilterReport
from app.domain.shipment import ShipmentNumber


class AssemblyReader(Protocol):
    def read(self, path: Path) -> list[ShipmentNumber]: ...


class TicketReader(Protocol):
    def read(self, path: Path) -> list[ShipmentNumber | None]: ...


class PageWriter(Protocol):
    def write(self, source: Path, indices: Iterable[int], output: Path) -> None: ...


class FilterRunner(Protocol):
    def filter(self, assembly: Path, ticket: Path, output: Path) -> FilterReport: ...
