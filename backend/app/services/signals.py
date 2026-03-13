from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Alert, ProductionRecord


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

        latest = history[0].oil_bbl + (history[0].gas_mcf / 6)
        trailing = [history[i].oil_bbl + (history[i].gas_mcf / 6) for i in range(1, 4)]
        trailing_avg = sum(trailing) / len(trailing)
        if trailing_avg <= 0:
            continue

        drop_pct = ((trailing_avg - latest) / trailing_avg) * 100
        if drop_pct < 40:
            continue

        source_url = history[0].source_url or f"internal://production_records/{asset_id}/{history[0].period_date.isoformat()}"
        source_url = f"{source_url}#production-collapse"
        if _alert_exists(db, "Production collapse", source_url):
            continue

        db.add(
            Alert(
                asset_id=asset_id,
                signal_type="Production collapse",
                severity="high" if drop_pct >= 60 else "medium",
                title="Production collapse detected",
                why_fired=f"Latest full month output is down {drop_pct:.1f}% versus trailing 3-month average.",
                event_date=history[0].period_date,
                source_url=source_url,
            )
        )
        created += 1

    db.commit()
    return created


def generate_inactivity_alerts(db: Session, gap_days: int = 60) -> int:
    records = db.scalars(select(ProductionRecord).order_by(ProductionRecord.asset_id, ProductionRecord.period_date.desc())).all()
    by_asset: dict[int, list[ProductionRecord]] = defaultdict(list)
    for rec in records:
        by_asset[rec.asset_id].append(rec)

    created = 0
    for asset_id, history in by_asset.items():
        if len(history) < 2:
            continue

        latest_period = history[0].period_date
        prior_period = history[1].period_date
        has_prior_production = any((rec.oil_bbl + rec.gas_mcf) > 0 for rec in history[1:])
        if not has_prior_production:
            continue

        gap = (latest_period - prior_period).days
        if gap < gap_days:
            continue

        source_url = history[0].source_url or f"internal://production_records/{asset_id}/{latest_period.isoformat()}"
        source_url = f"{source_url}#inactivity"
        if _alert_exists(db, "Inactivity / shut-in proxy", source_url):
            continue

        periods_without_reports = max(2, round(gap / 30))
        db.add(
            Alert(
                asset_id=asset_id,
                signal_type="Inactivity / shut-in proxy",
                severity="medium",
                title="Potential inactivity detected",
                why_fired=f"Asset appears to have {periods_without_reports} consecutive missing production periods after prior output.",
                event_date=latest_period,
                source_url=source_url,
            )
        )
        created += 1

    db.commit()
    return created


def run_signal_evaluation(db: Session) -> int:
    production = generate_production_collapse_alerts(db)
    inactivity = generate_inactivity_alerts(db)
    return production + inactivity


def send_email_digest(alerts: list[Alert]) -> None:
    _ = alerts
