from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.ingestion.base import IngestionStats
from app.ingestion.normalize import normalize_records
from app.ingestion.rrc_production import RRCTexasProductionIngestor

logger = logging.getLogger(__name__)


def run_rrc_production_ingestion(db: Session, source_url: str) -> IngestionStats:
    ingestor = RRCTexasProductionIngestor(source_url=source_url)
    stats = IngestionStats()

    csv_text = ingestor.fetch_csv()
    records, parse_failures = ingestor.parse_csv(csv_text)
    stats.fetched = len(csv_text.splitlines()) - 1 if csv_text else 0
    stats.parsed = len(records)
    stats.parse_failures = parse_failures

    normalize_records(db, records, stats)

    logger.info(
        "RRC ingestion completed",
        extra={
            "fetched": stats.fetched,
            "parsed": stats.parsed,
            "upserted_operators": stats.upserted_operators,
            "upserted_assets": stats.upserted_assets,
            "upserted_production_records": stats.upserted_production_records,
            "parse_failures": stats.parse_failures,
            "partial_failures": stats.partial_failures,
        },
    )
    return stats
