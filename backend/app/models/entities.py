from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Operator(Base):
    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    headquarters: Mapped[Optional[str]] = mapped_column(String(255))
    external_id: Mapped[Optional[str]] = mapped_column(String(100))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assets: Mapped[list["Asset"]] = relationship(back_populates="operator")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    county: Mapped[str] = mapped_column(String(100), nullable=False)
    field: Mapped[str] = mapped_column(String(100), nullable=False)
    basin: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    external_id: Mapped[Optional[str]] = mapped_column(String(100))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    operator: Mapped[Operator] = relationship(back_populates="assets")
    production_records: Mapped[list["ProductionRecord"]] = relationship(back_populates="asset")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="asset")


class ProductionRecord(Base):
    __tablename__ = "production_records"
    __table_args__ = (UniqueConstraint("asset_id", "period_date", name="uq_production_asset_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    period_date: Mapped[date] = mapped_column(Date, nullable=False)
    oil_bbl: Mapped[float] = mapped_column(Float, default=0)
    gas_mcf: Mapped[float] = mapped_column(Float, default=0)
    water_bbl: Mapped[float] = mapped_column(Float, default=0)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_record_id: Mapped[Optional[str]] = mapped_column(String(120))
    source_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)

    asset: Mapped[Asset] = relationship(back_populates="production_records")


class CourtCase(Base):
    __tablename__ = "court_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    debtor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    chapter: Mapped[str] = mapped_column(String(20), nullable=False)
    court_name: Mapped[str] = mapped_column(String(255), nullable=False)
    filed_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)

    docket_entries: Mapped[list["DocketEntry"]] = relationship(back_populates="court_case")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="court_case")


class DocketEntry(Base):
    __tablename__ = "docket_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    court_case_id: Mapped[int] = mapped_column(ForeignKey("court_cases.id"), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)

    court_case: Mapped[CourtCase] = relationship(back_populates="docket_entries")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.id"))
    court_case_id: Mapped[Optional[int]] = mapped_column(ForeignKey("court_cases.id"))
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    why_fired: Mapped[str] = mapped_column(Text, nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    asset: Mapped[Optional[Asset]] = relationship(back_populates="alerts")
    court_case: Mapped[Optional[CourtCase]] = relationship(back_populates="alerts")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["WatchlistItem"]] = relationship(back_populates="watchlist")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    watchlist: Mapped[Watchlist] = relationship(back_populates="items")
