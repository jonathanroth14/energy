from __future__ import annotations

import re

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Alert, CourtCase, DocketEntry, Operator, WatchlistItem

SALE_KEYWORDS = ["363", "sale motion", "asset purchase agreement", "apa", "stalking horse", "bid procedures"]


def _normalize_name(name: str) -> str:
    lowered = name.lower()
    cleaned = re.sub(r"[^a-z0-9 ]", " ", lowered)
    tokens = [t for t in cleaned.split() if t not in {"llc", "inc", "ltd", "lp", "corp", "co", "company", "energy"}]
    return " ".join(tokens)


def _alert_exists(db: Session, signal_type: str, source_url: str) -> bool:
    stmt = select(Alert.id).where(and_(Alert.signal_type == signal_type, Alert.source_url == source_url))
    return db.scalar(stmt) is not None


def generate_new_bankruptcy_filing_alerts(db: Session) -> int:
    created = 0
    for case in db.scalars(select(CourtCase)).all():
        if case.chapter not in {"Chapter 11", "Chapter 7"}:
            continue
        source_url = f"{case.source_url}#new-filing"
        if _alert_exists(db, "New bankruptcy filing", source_url):
            continue

        db.add(
            Alert(
                court_case_id=case.id,
                signal_type="New bankruptcy filing",
                severity="high",
                title=f"{case.chapter} filing: {case.debtor_name}",
                why_fired=f"Detected new {case.chapter} bankruptcy filing for a Texas energy-related debtor.",
                event_date=case.filed_date,
                source_url=source_url,
            )
        )
        created += 1

    db.commit()
    return created


def generate_asset_sale_motion_alerts(db: Session) -> int:
    created = 0
    for docket in db.scalars(select(DocketEntry)).all():
        content = f"{docket.title} {docket.content}".lower()
        if not any(k in content for k in SALE_KEYWORDS):
            continue

        source_url = f"{docket.source_url}#sale-motion"
        if _alert_exists(db, "Asset sale motion keyword hit", source_url):
            continue

        db.add(
            Alert(
                court_case_id=docket.court_case_id,
                signal_type="Asset sale motion keyword hit",
                severity="medium",
                title="Asset sale motion keyword detected",
                why_fired="Docket entry matched sale-process keywords (363, sale motion, APA, stalking horse, bid procedures).",
                event_date=docket.entry_date,
                source_url=source_url,
            )
        )
        created += 1

    db.commit()
    return created


def generate_watchlist_bankruptcy_match_alerts(db: Session) -> int:
    watched_operator_ids = {item.asset.operator_id for item in db.query(WatchlistItem).join(WatchlistItem.asset).all()}
    if not watched_operator_ids:
        return 0

    watched_operator_names = [_normalize_name(op.name) for op in db.scalars(select(Operator).where(Operator.id.in_(watched_operator_ids))).all()]

    created = 0
    for case in db.scalars(select(CourtCase)).all():
        debtor = _normalize_name(case.debtor_name)
        if not debtor or not any(name and (name in debtor or debtor in name) for name in watched_operator_names):
            continue

        source_url = f"{case.source_url}#watchlist-match"
        if _alert_exists(db, "Watchlist bankruptcy match", source_url):
            continue

        db.add(
            Alert(
                court_case_id=case.id,
                signal_type="Watchlist bankruptcy match",
                severity="high",
                title=f"Watchlist debtor match: {case.debtor_name}",
                why_fired="Debtor name matched one or more watched operators/assets.",
                event_date=case.filed_date,
                source_url=source_url,
            )
        )
        created += 1

    db.commit()
    return created


def run_bankruptcy_signal_evaluation(db: Session) -> int:
    a = generate_new_bankruptcy_filing_alerts(db)
    b = generate_asset_sale_motion_alerts(db)
    c = generate_watchlist_bankruptcy_match_alerts(db)
    return a + b + c
