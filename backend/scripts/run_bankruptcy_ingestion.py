import argparse
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.ingestion import run_courtlistener_bankruptcy_ingestion
from app.services.bankruptcy_signals import run_bankruptcy_signal_evaluation

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CourtListener bankruptcy ingestion and alert generation")
    parser.add_argument("--cases-source", default=settings.courtlistener_cases_source_url)
    parser.add_argument("--dockets-source", default=settings.courtlistener_dockets_source_url)
    parser.add_argument("--skip-signals", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        stats = run_courtlistener_bankruptcy_ingestion(
            db,
            cases_source=args.cases_source,
            dockets_source=args.dockets_source,
        )
        print(
            f"Bankruptcy ingestion complete: parsed_cases={stats.parsed_cases}, parsed_dockets={stats.parsed_dockets}, "
            f"upserted_cases={stats.upserted_cases}, upserted_dockets={stats.upserted_dockets}, "
            f"parse_failures={stats.parse_failures}, partial_failures={stats.partial_failures}"
        )

        if not args.skip_signals:
            alerts_created = run_bankruptcy_signal_evaluation(db)
            print(f"Bankruptcy signals complete: alerts_created={alerts_created}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
