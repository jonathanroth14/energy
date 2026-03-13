from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import AssetDetailOut, AssetOut
from app.services.assets import get_asset, list_assets

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetOut])
def get_assets(db: Session = Depends(get_db)):
    return list_assets(db)


@router.get("/{asset_id}", response_model=AssetDetailOut)
def get_asset_by_id(asset_id: int, db: Session = Depends(get_db)):
    asset = get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
