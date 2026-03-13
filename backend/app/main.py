import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.api.alerts import router as alerts_router
from app.api.assets import router as assets_router
from app.api.watchlists import router as watchlists_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.ingestion import run_courtlistener_bankruptcy_ingestion
from app.services.bankruptcy_signals import run_bankruptcy_signal_evaluation
from app.services.signals import run_signal_evaluation

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

app.include_router(alerts_router)
app.include_router(assets_router)
app.include_router(watchlists_router)

scheduler = BackgroundScheduler()


def scheduled_signal_job() -> None:
    db = SessionLocal()
    try:
        created = run_signal_evaluation(db)
        logger.info("Production signal job completed", extra={"alerts_created": created})
    finally:
        db.close()


def scheduled_bankruptcy_job() -> None:
    db = SessionLocal()
    try:
        try:
            run_courtlistener_bankruptcy_ingestion(
                db,
                settings.courtlistener_cases_source_url,
                settings.courtlistener_dockets_source_url,
            )
        except Exception as exc:
            logger.exception("Bankruptcy ingestion job failed", extra={"error": str(exc)})

        created = run_bankruptcy_signal_evaluation(db)
        logger.info("Bankruptcy signal job completed", extra={"alerts_created": created})
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    scheduler.add_job(scheduled_signal_job, "interval", minutes=60, id="signal_job", replace_existing=True)
    scheduler.add_job(scheduled_bankruptcy_job, "interval", minutes=120, id="bankruptcy_job", replace_existing=True)
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    scheduler.shutdown(wait=False)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
