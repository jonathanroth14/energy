from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from app.api.alerts import router as alerts_router
from app.api.assets import router as assets_router
from app.api.watchlists import router as watchlists_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.signals import run_signal_evaluation

app = FastAPI(title=settings.app_name)

app.include_router(alerts_router)
app.include_router(assets_router)
app.include_router(watchlists_router)

scheduler = BackgroundScheduler()


def scheduled_signal_job() -> None:
    db = SessionLocal()
    try:
        run_signal_evaluation(db)
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    scheduler.add_job(scheduled_signal_job, "interval", minutes=60, id="signal_job", replace_existing=True)
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    scheduler.shutdown(wait=False)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
