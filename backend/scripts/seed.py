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


def month_start(months_ago: int) -> date:
    today = date.today().replace(day=1)
    return today - timedelta(days=30 * months_ago)


def run() -> None:
    db = SessionLocal()
    try:
        for model in [WatchlistItem, Watchlist, Alert, DocketEntry, CourtCase, ProductionRecord, Asset, Operator]:
            db.execute(delete(model))
        db.commit()

        operator_names = [
            "Blue Mesa Operating",
            "Lone Star Petroleum Partners",
            "Rio Bend Energy",
            "Permian Crest Resources",
            "Karnes Basin Exploration",
            "West Fork Oil & Gas",
            "Red River Production Co",
            "Coyote Draw Energy",
            "Pioneer Hill Resources",
            "Mustang Ridge Operating",
        ]
        operators = [
            Operator(
                name=name,
                headquarters="Houston, TX",
                source_url="https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/",
                source_metadata={"seed": True, "dataset": "frontier-radar-demo"},
            )
            for name in operator_names
        ]
        db.add_all(operators)
        db.flush()

        counties = ["Midland", "Reeves", "Howard", "Karnes", "La Salle"]
        fields = ["Spraberry", "Wolfcamp", "Bone Spring", "Eagle Ford", "Yates"]
        assets: list[Asset] = []
        for i in range(25):
            assets.append(
                Asset(
                    operator_id=operators[i % len(operators)].id,
                    name=f"{['Mustang', 'Falcon', 'Mesa', 'Coyote', 'Pioneer'][i % 5]} Unit {i + 1}",
                    county=counties[i % len(counties)],
                    field=fields[i % len(fields)],
                    basin="Permian" if i % 2 == 0 else "Eagle Ford",
                    status="active" if i % 6 else "watch",
                    source_url="https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(assets)
        db.flush()

        production_records: list[ProductionRecord] = []

        # Scenario 1: production collapse (asset 1)
        collapse_asset = assets[0]
        for idx, oil in enumerate([110, 340, 355, 330]):
            period = month_start(idx)
            production_records.append(
                ProductionRecord(
                    asset_id=collapse_asset.id,
                    period_date=period,
                    oil_bbl=oil,
                    gas_mcf=1600,
                    water_bbl=120,
                    source_url="https://www.rrc.texas.gov/media/f4wifn4v/oil-gas-production-data.xlsx",
                    source_record_id=f"demo-collapse-{collapse_asset.id}-{period.isoformat()}",
                    source_metadata={"seed_scenario": "production-collapse"},
                )
            )

        # Scenario 2: inactivity (asset 2)
        inactivity_asset = assets[1]
        inactivity_periods = [month_start(0), month_start(3), month_start(4)]
        inactivity_oil = [0, 260, 255]
        for period, oil in zip(inactivity_periods, inactivity_oil):
            production_records.append(
                ProductionRecord(
                    asset_id=inactivity_asset.id,
                    period_date=period,
                    oil_bbl=oil,
                    gas_mcf=1200,
                    water_bbl=95,
                    source_url="https://www.rrc.texas.gov/media/f4wifn4v/oil-gas-production-data.xlsx",
                    source_record_id=f"demo-inactive-{inactivity_asset.id}-{period.isoformat()}",
                    source_metadata={"seed_scenario": "inactivity"},
                )
            )

        # General coverage records so dashboard/feed looks populated
        for i in range(43):
            asset = assets[(i + 2) % len(assets)]
            period = month_start((i % 4) + 1)
            production_records.append(
                ProductionRecord(
                    asset_id=asset.id,
                    period_date=period,
                    oil_bbl=max(80, 620 - i * 7),
                    gas_mcf=max(400, 3100 - i * 21),
                    water_bbl=140 + i,
                    source_url="https://www.rrc.texas.gov/media/f4wifn4v/oil-gas-production-data.xlsx",
                    source_record_id=f"demo-{asset.id}-{period.isoformat()}",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(production_records)

        # Bankruptcy cases: include one explicit chapter 11 tied to a watched operator-like debtor
        cases = [
            CourtCase(
                debtor_name="Blue Mesa Operating LLC",
                chapter="Chapter 11",
                court_name="US Bankruptcy Court SDTX",
                filed_date=month_start(0),
                source_url="https://www.courtlistener.com/docket/220100/blue-mesa-operating-llc/",
                external_case_id="220100",
                source_provider="courtlistener",
                source_metadata={"seed_scenario": "chapter-11"},
            )
        ]
        for i in range(2, 6):
            cases.append(
                CourtCase(
                    debtor_name=f"Texas Energy Debtor {i}",
                    chapter="Chapter 11" if i % 2 else "Chapter 7",
                    court_name="US Bankruptcy Court SDTX",
                    filed_date=month_start(0) - timedelta(days=i * 5),
                    source_url=f"https://www.courtlistener.com/docket/22010{i}/debtor-{i}/",
                    external_case_id=f"22010{i}",
                    source_provider="courtlistener",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(cases)
        db.flush()

        # Docket entries include sale-motion keywords
        dockets = [
            DocketEntry(
                court_case_id=cases[0].id,
                entry_date=month_start(0) + timedelta(days=5),
                title="Motion for approval of sale under 11 U.S.C. §363",
                content="Debtor seeks approval of sale motion, asset purchase agreement (APA), stalking horse protections and bid procedures.",
                source_url="https://www.courtlistener.com/docket/220100/15/motion-for-sale/",
                external_docket_id="880015",
                source_provider="courtlistener",
                source_metadata={"seed_scenario": "sale-motion-hit"},
            )
        ]
        keywords = ["363", "sale motion", "asset purchase agreement", "APA", "stalking horse", "bid procedures"]
        for i in range(2, 21):
            dockets.append(
                DocketEntry(
                    court_case_id=cases[(i - 1) % len(cases)].id,
                    entry_date=month_start(0) - timedelta(days=i),
                    title=f"Docket Entry {i}",
                    content=f"Includes {keywords[i % len(keywords)]} discussion for case review.",
                    source_url=f"https://example.com/dockets/{i}",
                    external_docket_id=f"seed-docket-{i}",
                    source_provider="seed",
                    source_metadata={"seed": True},
                )
            )
        db.add_all(dockets)

        # Base alerts for feed volume + all have valid id/detail route once inserted
        base_alerts = []
        scenario_types = [
            "Production collapse",
            "Inactivity / shut-in proxy",
            "New bankruptcy filing",
            "Asset sale motion keyword hit",
            "Watchlist bankruptcy match",
        ]
        severities = ["high", "medium", "high", "medium", "high"]
        for i in range(25):
            signal = scenario_types[i % len(scenario_types)]
            asset_ref = assets[i % len(assets)] if signal in {"Production collapse", "Inactivity / shut-in proxy"} else None
            case_ref = cases[i % len(cases)] if signal in {"New bankruptcy filing", "Asset sale motion keyword hit", "Watchlist bankruptcy match"} else None
            base_alerts.append(
                Alert(
                    asset_id=asset_ref.id if asset_ref else None,
                    court_case_id=case_ref.id if case_ref else None,
                    signal_type=signal,
                    severity=severities[i % len(severities)],
                    title=f"{signal}: demo event {i + 1}",
                    why_fired="Demo alert seeded for realistic feed coverage and walkthrough reliability.",
                    event_date=month_start(0) - timedelta(days=i),
                    source_url=f"https://demo.frontierradar.local/alerts/source/{i + 1}",
                )
            )
        db.add_all(base_alerts)

        watchlists = [
            Watchlist(name="Permian Distress", description="Distressed PDP opportunities in Midland/Reeves"),
            Watchlist(name="Bankruptcy Tracker", description="Texas Chapter 11/7 events with transaction potential"),
        ]
        db.add_all(watchlists)
        db.flush()

        # Ensure watchlist match scenario is possible (watchlist includes Blue Mesa operator assets)
        tracked_asset_indexes = [0, 1, 2, 3, 5, 8, 12, 15]
        for idx, asset_index in enumerate(tracked_asset_indexes):
            db.add(
                WatchlistItem(
                    watchlist_id=watchlists[idx % 2].id,
                    asset_id=assets[asset_index].id,
                    notes="Seeded tracked entity for demo walk-through",
                )
            )

        db.commit()

        created_production = run_signal_evaluation(db)
        created_bankruptcy = run_bankruptcy_signal_evaluation(db)
        print(f"Seed complete: production alerts={created_production}, bankruptcy alerts={created_bankruptcy}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
