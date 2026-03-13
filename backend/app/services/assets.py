from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Asset


def list_assets(db: Session) -> list[Asset]:
    return list(db.scalars(select(Asset).order_by(Asset.id)).all())


def get_asset(db: Session, asset_id: int) -> Asset | None:
    stmt = (
        select(Asset)
        .where(Asset.id == asset_id)
        .options(selectinload(Asset.production_records), selectinload(Asset.alerts))
    )
    return db.scalars(stmt).first()
