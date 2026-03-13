from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Alert, CourtCase, DocketEntry, ProductionRecord

SALE_KEYWORDS = ["363", "sale motion", "asset purchase agreement", "apa", "stalking horse", "bid procedures"]


def _alert_exists(db: Session, signal_type: str, source_url: str) -> bool:
    stmt = select(Alert.id).where(and_(Alert.signal_type == signal_type, Alert.source_url == source_url))
    return db.scalar(stmt) is not None


def generate_production_collapse_alerts(db: Session) -> int:
    records = db.scalars(select(ProductionRecord).order_by(ProductionRecord.asset_id, ProductionRecord.period_date.desc())).all()
    by_asset: dict[int, list[ProductionRecord]] = defaultdict(list)
    for rec in records:
        by_asset[rec.asset_id].append(rec)

    created = 0
    for asset_id, history in by_asset.items():
        if len(history) < 4:
            continue
        latest = history[0].oil_bbl
        trailing = [history[i].oil_bbl for i in range(1, 4)]
        trailing_avg = sum(trailing) / len(trailing)
        if trailing_avg <= 0:
            continue
        drop_pct = ((trailing_avg - latest) / trailing_avg) * 100
        if drop_pct >= 40:
            source_url = f"internal://production_records/{asset_id}/{history[0].period_date.isoformat()}"
            if _alert_exists(db, "Production collapse", source_url):
                continue
            db.add(
                Alert(
                    asset_id=asset_id,
                    signal_type="Production collapse",
                    severity="high" if drop_pct >= 60 else "medium",
                    title="Production collapse detected",
                    why_fired=f"Latest full month oil volume is down {drop_pct:.1f}% vs trailing 3-month average.",
                    event_date=history[0].period_date,
                    source_url=source_url,
                )
            )
            created += 1

    db.commit()
    return created


def generate_bankruptcy_alerts(db: Session) -> int:
    cases = db.scalars(select(CourtCase)).all()
    created = 0
    for case in cases:
        if case.chapter not in {"Chapter 11", "Chapter 7"}:
            continue
        if _alert_exists(db, "New bankruptcy filing", case.source_url):
            continue
        db.add(
            Alert(
                court_case_id=case.id,
                signal_type="New bankruptcy filing",
                severity="high",
                title=f"{case.chapter} filing: {case.debtor_name}",
                why_fired=f"Detected new {case.chapter} bankruptcy filing in {case.court_name}.",
                event_date=case.filed_date,
                source_url=case.source_url,
            )
        )
        created += 1
    db.commit()
    return created


def generate_sale_motion_alerts(db: Session) -> int:
    entries = db.scalars(select(DocketEntry)).all()
    created = 0
    for entry in entries:
        content = f"{entry.title} {entry.content}".lower()
        if not any(keyword in content for keyword in SALE_KEYWORDS):
            continue
        if _alert_exists(db, "Asset sale motion keyword hit", entry.source_url):
            continue
        db.add(
            Alert(
                court_case_id=entry.court_case_id,
                signal_type="Asset sale motion keyword hit",
                severity="medium",
                title="Asset sale process signal detected",
                why_fired="Docket text contains sale-process keywords (e.g., 363, APA, stalking horse, bid procedures).",
                event_date=entry.entry_date,
                source_url=entry.source_url,
            )
        )
        created += 1
    db.commit()
    return created


def run_signal_evaluation(db: Session) -> int:
    production = generate_production_collapse_alerts(db)
    bankruptcy = generate_bankruptcy_alerts(db)
    sale = generate_sale_motion_alerts(db)
    return production + bankruptcy + sale


def send_email_digest(alerts: list[Alert]) -> None:
    # Resend integration point: batch and send when email credentials are configured.
    _ = alerts
