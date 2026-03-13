from datetime import date

from sqlalchemy.orm import Session

from app.models import Alert


def run_signal_evaluation(db: Session) -> int:
    """Placeholder hook for scheduled signal ingestion/evaluation.

    MVP keeps alert generation seed-driven, but this function is where live source ingestion
    and rules engine execution are wired for production.
    """
    return db.query(Alert).count()


def send_email_digest(alerts: list[Alert]) -> None:
    """Resend integration hook for email alerts."""
    _ = alerts
    return None
