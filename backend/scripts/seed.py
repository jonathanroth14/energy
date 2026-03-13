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

        operators = [Operator(name=f"Operator {i}", headquarters="Houston, TX") for i in range(1, 11)]
        db.add_all(operators)
        db.flush()

        assets = []
        for i in range(1, 26):
            assets.append(
                Asset(
                    operator_id=operators[(i - 1) % len(operators)].id,
                    name=f"Asset {i}",
                    county=COUNTIES[i % len(COUNTIES)],
                    field=FIELDS[i % len(FIELDS)],
                    basin="Permian" if i % 2 == 0 else "Eagle Ford",
                    status="active" if i % 5 != 0 else "watch",
                )
            )
        db.add_all(assets)
        db.flush()

        production_records = []
        today = date.today().replace(day=1)
        for i in range(50):
            asset = assets[i % len(assets)]
            period = today - timedelta(days=30 * (i % 4 + 1))
            production_records.append(
                ProductionRecord(
                    asset_id=asset.id,
                    period_date=period,
                    oil_bbl=max(0, 500 - i * 4),
                    gas_mcf=max(0, 3000 - i * 11),
                    water_bbl=120 + i,
                )
            )
        db.add_all(production_records)

        cases = []
        for i in range(1, 6):
            cases.append(
                CourtCase(
                    debtor_name=f"Texas Energy Debtor {i}",
                    chapter="Chapter 11" if i % 2 else "Chapter 7",
                    court_name="US Bankruptcy Court SDTX",
                    filed_date=today - timedelta(days=10 * i),
                    source_url=f"https://example.com/cases/{i}",
                )
            )
        db.add_all(cases)
        db.flush()

        docket_entries = []
        keywords = ["363", "sale motion", "asset purchase agreement", "APA", "stalking horse", "bid procedures"]
        for i in range(1, 21):
            docket_entries.append(
                DocketEntry(
                    court_case_id=cases[(i - 1) % len(cases)].id,
                    entry_date=today - timedelta(days=i),
                    title=f"Docket Entry {i}",
                    content=f"Includes {keywords[i % len(keywords)]} details for case {i}",
                    source_url=f"https://example.com/dockets/{i}",
                )
            )
        db.add_all(docket_entries)

        alerts = []
        for i in range(1, 31):
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
                    why_fired="Rule matched based on month-over-month decline, inactivity window, bankruptcy chapter hit, or sale motion keyword.",
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
        print("Seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    run()
