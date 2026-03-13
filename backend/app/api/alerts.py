from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import AlertOut
from app.services.alerts import AlertFilters, get_alert, list_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def get_alerts(
    county: str | None = None,
    field: str | None = None,
    operator: str | None = None,
    signal_type: str | None = None,
    severity: str | None = None,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    filters = AlertFilters(county, field, operator, signal_type, severity, start_date, end_date)
    return list_alerts(db, filters)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert_by_id(alert_id: int, db: Session = Depends(get_db)):
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
