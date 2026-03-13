from datetime import date, timedelta

from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models import (
    Alert,
    Asset,
    CourtCase,
    DocketEntry,
    Operator,
    ProductionRecord,
    Watchlist,
    WatchlistItem,
)
from app.services.bankruptcy_signals import run_bankruptcy_signal_evaluation
from app.services.signals import run_signal_evaluation

SIGNAL_TYPES = [
    "Production collapse",
    "Inactivity / shut-in proxy",
    "New bankruptcy filing",
    "Asset sale motion keyword hit",
]
SEVERITIES = ["low", "medium", "high"]
COUNTIES = ["Midland", "Reeves", "Howard", "Karnes", "La Salle"]
FIELDS = ["Spraberry", "Wolfcamp", "Eagle Ford", "Bone Spring", "Yates"]


def run() -> None:
    db = SessionLocal()
    try:
        for model in [WatchlistItem, Watchlist, Alert, DocketEntry, CourtCase, ProductionRecord, Asset, Operator]:
            db.execute(delete(model))
        db.commit()

        operators = [
            Operator(name=f"Operator {i}", headquarters="Houston, TX", source_url="https://www.rrc.texas.gov/", source_metadata={"seed": True})
            for i in range(1, 11)
        ]
        db.add_all(operators)
        db.flush()

        assets: list[Asset] = []
        for i in range(1, 26):
            assets.append(
                Asset(
                    operator_id=operators[(i - 1) % len(operators)].id,
                    name=f"Asset {i}",
                    county=COUNTIES[i % len(COUNTIES)],
                    field=FIELDS[i % len(FIELDS)],
                    basin="Permian" if i % 2 == 0 else "Eagle Ford",
                    status="active" if i % 5 != 0 else "watch",
                    source_url="https://www.rrc.texas.gov/",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(assets)
        db.flush()

        today = date.today().replace(day=1)
        production_records: list[ProductionRecord] = []

        # Alert demonstration pattern 1: production collapse for asset 1
        collapse_months = [today - timedelta(days=30 * i) for i in range(4)]
        collapse_values = [120.0, 300.0, 320.0, 310.0]
        for period, oil in zip(collapse_months, collapse_values):
            production_records.append(
                ProductionRecord(
                    asset_id=assets[0].id,
                    period_date=period,
                    oil_bbl=oil,
                    gas_mcf=1200,
                    water_bbl=100,
                    source_url="https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/",
                    source_record_id=f"seed-collapse-{period.isoformat()}",
                    source_metadata={"seed": "collapse-demo"},
                )
            )

        # Alert demonstration pattern 2: inactivity for asset 2 (gap >= 60 days)
        inactivity_periods = [today, today - timedelta(days=90), today - timedelta(days=120)]
        inactivity_oil = [0.0, 260.0, 270.0]
        for period, oil in zip(inactivity_periods, inactivity_oil):
            production_records.append(
                ProductionRecord(
                    asset_id=assets[1].id,
                    period_date=period,
                    oil_bbl=oil,
                    gas_mcf=1500,
                    water_bbl=110,
                    source_url="https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/",
                    source_record_id=f"seed-inactivity-{period.isoformat()}",
                    source_metadata={"seed": "inactivity-demo"},
                )
            )

        # Remaining records to keep realistic volume
        for i in range(43):
            asset = assets[(i + 2) % len(assets)]
            period = today - timedelta(days=30 * (i % 4 + 1))
            production_records.append(
                ProductionRecord(
                    asset_id=asset.id,
                    period_date=period,
                    oil_bbl=max(0, 500 - i * 4),
                    gas_mcf=max(0, 3000 - i * 11),
                    water_bbl=120 + i,
                    source_url="https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/",
                    source_record_id=f"seed-{asset.id}-{period.isoformat()}",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(production_records)

        cases = [
            CourtCase(
                debtor_name="Operator 1 Energy LLC",
                chapter="Chapter 11",
                court_name="US Bankruptcy Court SDTX",
                filed_date=today - timedelta(days=10),
                source_url="https://www.courtlistener.com/docket/1001/operator-1-energy-llc/",
                external_case_id="1001",
                source_provider="courtlistener",
                source_metadata={"seed": "chapter11-watchlist"},
            )
        ]
        for i in range(2, 6):
            cases.append(
                CourtCase(
                    debtor_name=f"Texas Energy Debtor {i}",
                    chapter="Chapter 11" if i % 2 else "Chapter 7",
                    court_name="US Bankruptcy Court SDTX",
                    filed_date=today - timedelta(days=10 * i),
                    source_url=f"https://example.com/cases/{i}",
                    external_case_id=f"seed-case-{i}",
                    source_provider="seed",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(cases)
        db.flush()

        docket_entries = [
            DocketEntry(
                court_case_id=cases[0].id,
                entry_date=today - timedelta(days=3),
                title="Motion for approval of sale under 363",
                content="Debtor files sale motion with asset purchase agreement (APA) and stalking horse bid procedures.",
                source_url="https://www.courtlistener.com/docket/1001/5001/",
                external_docket_id="5001",
                source_provider="courtlistener",
                source_metadata={"seed": "sale-motion-hit"},
            )
        ]
        keywords = ["363", "sale motion", "asset purchase agreement", "APA", "stalking horse", "bid procedures"]
        for i in range(2, 21):
            docket_entries.append(
                DocketEntry(
                    court_case_id=cases[(i - 1) % len(cases)].id,
                    entry_date=today - timedelta(days=i),
                    title=f"Docket Entry {i}",
                    content=f"Includes {keywords[i % len(keywords)]} details for case {i}",
                    source_url=f"https://example.com/dockets/{i}",
                    external_docket_id=f"seed-docket-{i}",
                    source_provider="seed",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(docket_entries)

        alerts = []
        for i in range(1, 25):
            signal = SIGNAL_TYPES[(i - 1) % len(SIGNAL_TYPES)]
            asset_ref = assets[(i - 1) % len(assets)] if signal != "New bankruptcy filing" else None
            case_ref = cases[(i - 1) % len(cases)] if signal in ["New bankruptcy filing", "Asset sale motion keyword hit"] else None
            alerts.append(
                Alert(
                    asset_id=asset_ref.id if asset_ref else None,
                    court_case_id=case_ref.id if case_ref else None,
                    signal_type=signal,
                    severity=SEVERITIES[(i - 1) % len(SEVERITIES)],
                    title=f"{signal} detected #{i}",
                    why_fired="Seeded alert for demo feed coverage.",
                    event_date=today - timedelta(days=i),
                    source_url=f"https://example.com/source/{i}",
                )
            )
        db.add_all(alerts)

        watchlists = [
            Watchlist(name="Permian Distress", description="High-conviction distressed opportunities"),
            Watchlist(name="Bankruptcy Tracker", description="Texas court-driven opportunities"),
        ]
        db.add_all(watchlists)
        db.flush()

        for idx, asset in enumerate(assets[:8]):
            db.add(
                WatchlistItem(
                    watchlist_id=watchlists[idx % 2].id,
                    asset_id=asset.id,
                    notes="Initial seeded watchlist item",
                )
            )

        db.commit()

        generated_prod = run_signal_evaluation(db)
        generated_bankruptcy = run_bankruptcy_signal_evaluation(db)
        print(f"Seed complete; generated {generated_prod + generated_bankruptcy} rule-based alerts")
    finally:
        db.close()


if __name__ == "__main__":
    run()
