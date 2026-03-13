from datetime import date

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models import Alert, Asset, Operator


class AlertFilters:
    def __init__(
        self,
        county: str | None = None,
        operator: str | None = None,
        alert_type: str | None = None,
        severity: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self.county = county
        self.operator = operator
        self.alert_type = alert_type
        self.severity = severity
        self.start_date = start_date
        self.end_date = end_date


def list_alerts(db: Session, filters: AlertFilters) -> list[Alert]:
    query: Select[tuple[Alert]] = (
        select(Alert)
        .outerjoin(Asset, Alert.asset_id == Asset.id)
        .outerjoin(Operator, Asset.operator_id == Operator.id)
        .order_by(Alert.event_date.desc(), Alert.id.desc())
    )

    if filters.county:
        query = query.where(Asset.county.ilike(f"%{filters.county}%"))
    if filters.operator:
        query = query.where(Operator.name.ilike(f"%{filters.operator}%"))
    if filters.alert_type:
        query = query.where(Alert.signal_type == filters.alert_type)
    if filters.severity:
        query = query.where(Alert.severity == filters.severity)
    if filters.start_date:
        query = query.where(Alert.event_date >= filters.start_date)
    if filters.end_date:
        query = query.where(Alert.event_date <= filters.end_date)

    return list(db.scalars(query).all())


def get_alert(db: Session, alert_id: int) -> Alert | None:
    return db.get(Alert, alert_id)
