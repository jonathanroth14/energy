from __future__ import annotations

import csv
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests

from app.ingestion.base import SourceRecord

logger = logging.getLogger(__name__)


class RRCTexasProductionIngestor:
    """CSV ingestor for Texas RRC production exports.

    Uses an official/public downloadable RRC export URL configured by env var.
    The parser is defensive to handle slightly different column names.
    """

    def __init__(self, source_url: str, source_name: str = "Texas Railroad Commission"):
        self.source_url = source_url
        self.source_name = source_name

    def fetch_csv(self, timeout_s: int = 30) -> str:
        if self.source_url.startswith("file://"):
            path = Path(self.source_url.replace("file://", "", 1))
            text = path.read_text(encoding="utf-8")
            logger.info("Fetched RRC production source", extra={"source_url": self.source_url, "status": "local-file"})
            return text

        response = requests.get(self.source_url, timeout=timeout_s)
        response.raise_for_status()
        logger.info("Fetched RRC production source", extra={"source_url": self.source_url, "status": response.status_code})
        return response.text

    def parse_csv(self, csv_text: str) -> tuple[list[SourceRecord], int]:
        reader = csv.DictReader(io.StringIO(csv_text))
        records: list[SourceRecord] = []
        failures = 0
        for row in reader:
            try:
                period = self._parse_period(self._first(row, "production_month", "period_date", "month"))
                operator_name = self._first(row, "operator_name", "operator")
                asset_name = self._first(row, "lease_name", "asset_name", "lease")
                county = self._first(row, "county", "county_name")
                field = self._first(row, "field", "field_name")
                basin = self._first(row, "basin", "district", default="Texas")

                oil_bbl = float(self._first(row, "oil_bbl", "oil_production", default="0") or 0)
                gas_mcf = float(self._first(row, "gas_mcf", "gas_production", default="0") or 0)
                water_bbl = float(self._first(row, "water_bbl", "water_production", default="0") or 0)

                source_record_id = self._first(row, "record_id", "api", "lease_id", default="")
                if not source_record_id:
                    source_record_id = f"{operator_name}:{asset_name}:{period.isoformat()}"

                records.append(
                    SourceRecord(
                        source_record_id=source_record_id,
                        source_url=self.source_url,
                        source_name=self.source_name,
                        source_metadata={"raw": {k: v for k, v in row.items() if v not in (None, "")}},
                        operator_name=operator_name,
                        asset_name=asset_name,
                        county=county,
                        field=field,
                        basin=basin,
                        period_date=period,
                        oil_bbl=oil_bbl,
                        gas_mcf=gas_mcf,
                        water_bbl=water_bbl,
                    )
                )
            except Exception as exc:  # parse failure logging requirement
                failures += 1
                logger.warning("Parse failure for RRC row", extra={"error": str(exc), "row": row})
        logger.info("Parsed RRC rows", extra={"parsed": len(records), "parse_failures": failures})
        return records, failures

    @staticmethod
    def _first(row: dict[str, str], *keys: str, default: str | None = None) -> str:
        for key in keys:
            for candidate in (key, key.upper(), key.lower()):
                if candidate in row and row[candidate] not in (None, ""):
                    return str(row[candidate]).strip()
        if default is not None:
            return default
        raise ValueError(f"Missing required columns {keys}")

    @staticmethod
    def _parse_period(value: str) -> datetime.date:
        if len(value) == 7:  # YYYY-MM
            return datetime.strptime(f"{value}-01", "%Y-%m-%d").date()
        return datetime.strptime(value, "%Y-%m-%d").date()


def chunked(records: list[SourceRecord], chunk_size: int = 500) -> Iterable[list[SourceRecord]]:
    for i in range(0, len(records), chunk_size):
        yield records[i : i + chunk_size]
