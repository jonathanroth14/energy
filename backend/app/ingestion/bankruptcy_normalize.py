from __future__ import annotations

import logging

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.ingestion.bankruptcy_base import BankruptcyCaseRecord, BankruptcyDocketRecord, BankruptcyIngestionStats
from app.models import CourtCase, DocketEntry

logger = logging.getLogger(__name__)


def upsert_bankruptcy_cases(db: Session, cases: list[BankruptcyCaseRecord], stats: BankruptcyIngestionStats) -> dict[str, int]:
    case_id_map: dict[str, int] = {}
    for case in cases:
        try:
            db_case = db.scalar(
                select(CourtCase).where(
                    and_(
                        CourtCase.external_case_id == case.external_case_id,
                        CourtCase.source_provider == "courtlistener",
                    )
                )
            )
            if db_case is None:
                db_case = CourtCase(
                    external_case_id=case.external_case_id,
                    debtor_name=case.debtor_name,
                    chapter=case.chapter,
                    court_name=case.court_name,
                    filed_date=case.filed_date,
                    source_url=case.source_url,
                    source_provider="courtlistener",
                    source_metadata=case.source_metadata,
                )
                db.add(db_case)
                db.flush()
                stats.upserted_cases += 1
            else:
                db_case.debtor_name = case.debtor_name
                db_case.chapter = case.chapter
                db_case.court_name = case.court_name
                db_case.filed_date = case.filed_date
                db_case.source_url = case.source_url
                db_case.source_metadata = case.source_metadata

            case_id_map[case.external_case_id] = db_case.id
        except Exception as exc:
            stats.partial_failures += 1
            logger.exception("Partial failure upserting case", extra={"external_case_id": case.external_case_id, "error": str(exc)})

    db.commit()
    return case_id_map


def upsert_bankruptcy_dockets(
    db: Session,
    dockets: list[BankruptcyDocketRecord],
    case_id_map: dict[str, int],
    stats: BankruptcyIngestionStats,
) -> None:
    for docket in dockets:
        try:
            court_case_id = case_id_map.get(docket.external_case_id)
            if court_case_id is None:
                stats.partial_failures += 1
                logger.warning(
                    "Partial failure upserting docket: missing parent case",
                    extra={"external_docket_id": docket.external_docket_id, "external_case_id": docket.external_case_id},
                )
                continue

            db_docket = db.scalar(
                select(DocketEntry).where(
                    and_(
                        DocketEntry.external_docket_id == docket.external_docket_id,
                        DocketEntry.source_provider == "courtlistener",
                    )
                )
            )
            if db_docket is None:
                db_docket = DocketEntry(
                    court_case_id=court_case_id,
                    external_docket_id=docket.external_docket_id,
                    entry_date=docket.entry_date,
                    title=docket.title,
                    content=docket.content,
                    source_url=docket.source_url,
                    source_provider="courtlistener",
                    source_metadata=docket.source_metadata,
                )
                db.add(db_docket)
                stats.upserted_dockets += 1
            else:
                db_docket.court_case_id = court_case_id
                db_docket.entry_date = docket.entry_date
                db_docket.title = docket.title
                db_docket.content = docket.content
                db_docket.source_url = docket.source_url
                db_docket.source_metadata = docket.source_metadata
        except Exception as exc:
            stats.partial_failures += 1
            logger.exception("Partial failure upserting docket", extra={"external_docket_id": docket.external_docket_id, "error": str(exc)})

    db.commit()
