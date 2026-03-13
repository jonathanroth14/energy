from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Alert, Asset, Operator, ProductionRecord
from app.services.signals import run_signal_evaluation


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_generates_production_collapse_and_inactivity_alerts() -> None:
    db = _session()
    op = Operator(name="Test Operator")
    db.add(op)
    db.flush()

    collapse_asset = Asset(operator_id=op.id, name="Collapse", county="Midland", field="Spraberry", basin="Permian", status="active")
    inactive_asset = Asset(operator_id=op.id, name="Inactive", county="Howard", field="Wolfcamp", basin="Permian", status="active")
    db.add_all([collapse_asset, inactive_asset])
    db.flush()

    for month, oil in [(date(2026, 4, 1), 120), (date(2026, 3, 1), 300), (date(2026, 2, 1), 320), (date(2026, 1, 1), 330)]:
        db.add(ProductionRecord(asset_id=collapse_asset.id, period_date=month, oil_bbl=oil, gas_mcf=1200, water_bbl=100, source_url="https://rrc"))

    db.add(ProductionRecord(asset_id=inactive_asset.id, period_date=date(2026, 4, 1), oil_bbl=0, gas_mcf=0, water_bbl=20, source_url="https://rrc"))
    db.add(ProductionRecord(asset_id=inactive_asset.id, period_date=date(2026, 1, 1), oil_bbl=200, gas_mcf=1000, water_bbl=30, source_url="https://rrc"))

    db.commit()

    created = run_signal_evaluation(db)
    assert created >= 2

    signals = {a.signal_type for a in db.query(Alert).all()}
    assert "Production collapse" in signals
    assert "Inactivity / shut-in proxy" in signals
