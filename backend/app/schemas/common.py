from datetime import date
from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    asset_id: int | None
    signal_type: str
    severity: str
    title: str
    why_fired: str
    event_date: date
    source_url: str

    class Config:
        from_attributes = True


class ProductionRecordOut(BaseModel):
    period_date: date
    oil_bbl: float
    gas_mcf: float
    water_bbl: float

    class Config:
        from_attributes = True


class AssetOut(BaseModel):
    id: int
    operator_id: int
    name: str
    county: str
    field: str
    basin: str
    status: str

    class Config:
        from_attributes = True


class AssetDetailOut(AssetOut):
    production_records: list[ProductionRecordOut]
    alerts: list[AlertOut]


class WatchlistItemCreate(BaseModel):
    asset_id: int
    notes: str | None = None


class WatchlistCreate(BaseModel):
    name: str
    description: str | None = None


class WatchlistItemOut(BaseModel):
    id: int
    asset_id: int
    notes: str | None

    class Config:
        from_attributes = True


class WatchlistOut(BaseModel):
    id: int
    name: str
    description: str | None
    items: list[WatchlistItemOut] = []

    class Config:
        from_attributes = True
