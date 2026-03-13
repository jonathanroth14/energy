from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.ingestion.bankruptcy_base import BankruptcyIngestionStats
from app.ingestion.bankruptcy_normalize import upsert_bankruptcy_cases, upsert_bankruptcy_dockets
from app.ingestion.courtlistener_bankruptcy import CourtListenerBankruptcyIngestor

logger = logging.getLogger(__name__)


def run_courtlistener_bankruptcy_ingestion(db: Session, cases_source: str, dockets_source: str) -> BankruptcyIngestionStats:
    ingestor = CourtListenerBankruptcyIngestor(cases_source=cases_source, dockets_source=dockets_source)
    stats = BankruptcyIngestionStats()

    cases_payload = ingestor.fetch_json(cases_source)
    dockets_payload = ingestor.fetch_json(dockets_source)
    stats.fetched_cases = len(cases_payload.get("results", []))
    stats.fetched_dockets = len(dockets_payload.get("results", []))

    parsed_cases, case_failures = ingestor.parse_cases(cases_payload, cases_source)
    parsed_dockets, docket_failures = ingestor.parse_dockets(dockets_payload, dockets_source)
    stats.parsed_cases = len(parsed_cases)
    stats.parsed_dockets = len(parsed_dockets)
    stats.parse_failures = case_failures + docket_failures

    case_id_map = upsert_bankruptcy_cases(db, parsed_cases, stats)
    upsert_bankruptcy_dockets(db, parsed_dockets, case_id_map, stats)

    logger.info(
        "Bankruptcy ingestion completed",
        extra={
            "fetched_cases": stats.fetched_cases,
            "fetched_dockets": stats.fetched_dockets,
            "parsed_cases": stats.parsed_cases,
            "parsed_dockets": stats.parsed_dockets,
            "upserted_cases": stats.upserted_cases,
            "upserted_dockets": stats.upserted_dockets,
            "parse_failures": stats.parse_failures,
            "partial_failures": stats.partial_failures,
        },
    )
    return stats
