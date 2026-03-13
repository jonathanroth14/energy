from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.ingestion.base import IngestionStats, SourceRecord
from app.ingestion.normalize import normalize_records
from app.models import Asset, Operator, ProductionRecord


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_normalize_idempotent_upsert() -> None:
    db = _session()
    rec = SourceRecord(
        source_record_id="r-1",
        source_url="https://www.rrc.texas.gov/example.csv",
        source_name="RRC",
        source_metadata={"k": "v"},
        operator_name="Op A",
        asset_name="Lease 1",
        county="Midland",
        field="Spraberry",
        basin="Permian",
        period_date=date(2026, 3, 1),
        oil_bbl=100,
        gas_mcf=600,
        water_bbl=10,
    )

    stats = normalize_records(db, [rec], IngestionStats())
    assert stats.upserted_operators == 1
    assert stats.upserted_assets == 1
    assert stats.upserted_production_records == 1

    rec2 = SourceRecord(**{**rec.__dict__, "oil_bbl": 90})
    stats2 = normalize_records(db, [rec2], IngestionStats())
    assert db.query(Operator).count() == 1
    assert db.query(Asset).count() == 1
    assert db.query(ProductionRecord).count() == 1
    assert db.query(ProductionRecord).first().oil_bbl == 90
    assert stats2.upserted_production_records == 1
