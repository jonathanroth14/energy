from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int | None
    signal_type: str
    severity: str
    title: str
    why_fired: str
    event_date: date
    source_url: str


class ProductionRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period_date: date
    oil_bbl: float
    gas_mcf: float
    water_bbl: float


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    operator_id: int
    name: str
    county: str
    field: str
    basin: str
    status: str


class AssetDetailOut(AssetOut):
    production_records: list[ProductionRecordOut]
    alerts: list[AlertOut]


class WatchlistItemCreate(BaseModel):
    asset_id: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=1000)


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class WatchlistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    notes: str | None


class WatchlistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    items: list[WatchlistItemOut] = []
