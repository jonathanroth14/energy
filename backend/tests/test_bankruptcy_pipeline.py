from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.ingestion.bankruptcy_service import run_courtlistener_bankruptcy_ingestion
from app.models import Alert, Asset, Operator, Watchlist, WatchlistItem
from app.services.bankruptcy_signals import run_bankruptcy_signal_evaluation


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_bankruptcy_ingestion_and_alerts() -> None:
    db = _session()

    operator = Operator(name="Operator 1 Energy LLC")
    db.add(operator)
    db.flush()
    asset = Asset(operator_id=operator.id, name="Asset A", county="Midland", field="Spraberry", basin="Permian", status="active")
    db.add(asset)
    db.flush()
    watchlist = Watchlist(name="Distress")
    db.add(watchlist)
    db.flush()
    db.add(WatchlistItem(watchlist_id=watchlist.id, asset_id=asset.id))
    db.commit()

    root = Path(__file__).resolve().parents[1]
    cases_source = f"file://{root / 'scripts/data/sample_courtlistener_cases.json'}"
    dockets_source = f"file://{root / 'scripts/data/sample_courtlistener_dockets.json'}"

    stats = run_courtlistener_bankruptcy_ingestion(db, cases_source, dockets_source)
    assert stats.parsed_cases >= 1
    assert stats.parsed_dockets >= 1

    created = run_bankruptcy_signal_evaluation(db)
    assert created >= 3

    signal_types = {a.signal_type for a in db.query(Alert).all()}
    assert "New bankruptcy filing" in signal_types
    assert "Asset sale motion keyword hit" in signal_types
    assert "Watchlist bankruptcy match" in signal_types
