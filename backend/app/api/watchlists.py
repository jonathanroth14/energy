from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import (
    WatchlistCreate,
    WatchlistItemCreate,
    WatchlistItemOut,
    WatchlistOut,
)
from app.services.watchlists import add_watchlist_item, create_watchlist, list_watchlists

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.get("", response_model=list[WatchlistOut])
def get_watchlists(db: Session = Depends(get_db)):
    return list_watchlists(db)


@router.post("", response_model=WatchlistOut)
def post_watchlist(payload: WatchlistCreate, db: Session = Depends(get_db)):
    return create_watchlist(db, payload)


@router.post("/{watchlist_id}/items", response_model=WatchlistItemOut)
def post_watchlist_item(watchlist_id: int, payload: WatchlistItemCreate, db: Session = Depends(get_db)):
    return add_watchlist_item(db, watchlist_id, payload)
