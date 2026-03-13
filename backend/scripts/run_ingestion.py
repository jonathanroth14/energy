import argparse
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.ingestion import run_rrc_production_ingestion
from app.services.signals import run_signal_evaluation

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Frontier Radar ingestion and signal generation")
    parser.add_argument("--source-url", default=settings.rrc_production_source_url, help="RRC CSV source URL")
    parser.add_argument("--skip-signals", action="store_true", help="Skip signal generation after ingestion")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        stats = run_rrc_production_ingestion(db, args.source_url)
        print(
            f"Ingestion complete: parsed={stats.parsed}, "
            f"upserted_operators={stats.upserted_operators}, "
            f"upserted_assets={stats.upserted_assets}, "
            f"upserted_production_records={stats.upserted_production_records}, "
            f"parse_failures={stats.parse_failures}, partial_failures={stats.partial_failures}"
        )

        if not args.skip_signals:
            created = run_signal_evaluation(db)
            print(f"Signal generation complete: alerts_created={created}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
