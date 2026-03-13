from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import requests

from app.ingestion.bankruptcy_base import BankruptcyCaseRecord, BankruptcyDocketRecord

logger = logging.getLogger(__name__)


class CourtListenerBankruptcyIngestor:
    """Ingests bankruptcy case and docket events from CourtListener-compatible JSON.

    Assumptions:
    - CourtListener REST payload includes `results` arrays.
    - Case records provide debtor/case metadata and a stable ID.
    - Docket records include a stable entry ID plus a parent case ID.
    - This adapter is intentionally isolated so PACER-compatible sources can be added later.
    """

    def __init__(self, cases_source: str, dockets_source: str):
        self.cases_source = cases_source
        self.dockets_source = dockets_source

    def fetch_json(self, source_url: str, timeout_s: int = 30) -> dict:
        if source_url.startswith("file://"):
            path = Path(source_url.replace("file://", "", 1))
            payload = json.loads(path.read_text(encoding="utf-8"))
            logger.info("Fetched CourtListener source", extra={"source_url": source_url, "status": "local-file"})
            return payload

        response = requests.get(source_url, timeout=timeout_s)
        response.raise_for_status()
        logger.info("Fetched CourtListener source", extra={"source_url": source_url, "status": response.status_code})
        return response.json()

    def parse_cases(self, payload: dict, source_url: str) -> tuple[list[BankruptcyCaseRecord], int]:
        results = payload.get("results", [])
        records: list[BankruptcyCaseRecord] = []
        failures = 0
        for row in results:
            try:
                record = BankruptcyCaseRecord(
                    external_case_id=str(row.get("id") or row.get("case_id")),
                    debtor_name=str(row.get("debtor_name") or row.get("case_name") or "").strip(),
                    chapter=str(row.get("chapter") or "Unknown").strip(),
                    court_name=str(row.get("court_name") or row.get("court") or "Unknown Court").strip(),
                    filed_date=self._parse_date(row.get("filed_date") or row.get("date_filed")),
                    source_url=str(row.get("absolute_url") or row.get("url") or source_url),
                    source_metadata={"raw": row, "provider": "CourtListener"},
                )
                if not record.external_case_id or not record.debtor_name:
                    raise ValueError("Missing case id or debtor")
                records.append(record)
            except Exception as exc:
                failures += 1
                logger.warning("Case parse failure", extra={"error": str(exc), "row": row})

        logger.info("Parsed CourtListener cases", extra={"parsed": len(records), "parse_failures": failures})
        return records, failures

    def parse_dockets(self, payload: dict, source_url: str) -> tuple[list[BankruptcyDocketRecord], int]:
        results = payload.get("results", [])
        records: list[BankruptcyDocketRecord] = []
        failures = 0
        for row in results:
            try:
                record = BankruptcyDocketRecord(
                    external_docket_id=str(row.get("id") or row.get("docket_entry_id")),
                    external_case_id=str(row.get("docket") or row.get("case_id") or row.get("case")),
                    entry_date=self._parse_date(row.get("date_filed") or row.get("entry_date")),
                    title=str(row.get("short_description") or row.get("title") or "Docket entry").strip(),
                    content=str(row.get("description") or row.get("text") or "").strip(),
                    source_url=str(row.get("absolute_url") or row.get("url") or source_url),
                    source_metadata={"raw": row, "provider": "CourtListener"},
                )
                if not record.external_case_id or not record.external_docket_id:
                    raise ValueError("Missing docket id or case id")
                records.append(record)
            except Exception as exc:
                failures += 1
                logger.warning("Docket parse failure", extra={"error": str(exc), "row": row})

        logger.info("Parsed CourtListener dockets", extra={"parsed": len(records), "parse_failures": failures})
        return records, failures

    @staticmethod
    def _parse_date(value: str | None) -> datetime.date:
        if value is None:
            raise ValueError("Date missing")
        value = str(value)
        if len(value) >= 10:
            value = value[:10]
        return datetime.strptime(value, "%Y-%m-%d").date()
