from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Watchlist, WatchlistItem
from app.schemas.common import WatchlistCreate, WatchlistItemCreate


def list_watchlists(db: Session) -> list[Watchlist]:
    stmt = select(Watchlist).options(selectinload(Watchlist.items)).order_by(Watchlist.id)
    return list(db.scalars(stmt).all())


def create_watchlist(db: Session, payload: WatchlistCreate) -> Watchlist:
    watchlist = Watchlist(name=payload.name, description=payload.description)
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    return watchlist


def add_watchlist_item(db: Session, watchlist_id: int, payload: WatchlistItemCreate) -> WatchlistItem:
    item = WatchlistItem(watchlist_id=watchlist_id, asset_id=payload.asset_id, notes=payload.notes)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
