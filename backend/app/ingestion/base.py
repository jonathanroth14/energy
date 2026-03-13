from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class SourceRecord:
    source_record_id: str
    source_url: str
    source_name: str
    source_metadata: dict[str, Any]
    operator_name: str
    asset_name: str
    county: str
    field: str
    basin: str
    period_date: date
    oil_bbl: float
    gas_mcf: float
    water_bbl: float


@dataclass
class IngestionStats:
    fetched: int = 0
    parsed: int = 0
    upserted_operators: int = 0
    upserted_assets: int = 0
    upserted_production_records: int = 0
    parse_failures: int = 0
    partial_failures: int = 0
