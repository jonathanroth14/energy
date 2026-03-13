from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Asset, Watchlist, WatchlistItem
from app.schemas.common import WatchlistCreate, WatchlistItemCreate


def list_watchlists(db: Session) -> list[Watchlist]:
    stmt = select(Watchlist).options(selectinload(Watchlist.items)).order_by(Watchlist.id)
    return list(db.scalars(stmt).all())


def create_watchlist(db: Session, payload: WatchlistCreate) -> Watchlist:
    watchlist = Watchlist(name=payload.name.strip(), description=payload.description)
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    return watchlist


def add_watchlist_item(db: Session, watchlist_id: int, payload: WatchlistItemCreate) -> WatchlistItem:
    watchlist = db.get(Watchlist, watchlist_id)
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    asset = db.get(Asset, payload.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    existing = db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.asset_id == payload.asset_id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Asset already exists in watchlist")

    item = WatchlistItem(watchlist_id=watchlist_id, asset_id=payload.asset_id, notes=payload.notes)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
