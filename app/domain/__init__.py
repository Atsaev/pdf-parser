"""Доменные модели: номер отправления и отчёт о фильтрации."""

from app.domain.report import FilterReport
from app.domain.shipment import ShipmentNumber

__all__ = ["FilterReport", "ShipmentNumber"]
