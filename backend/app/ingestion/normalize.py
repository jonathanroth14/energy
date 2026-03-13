from __future__ import annotations

import logging

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.ingestion.base import IngestionStats, SourceRecord
from app.models import Asset, Operator, ProductionRecord

logger = logging.getLogger(__name__)


def normalize_records(db: Session, records: list[SourceRecord], stats: IngestionStats) -> IngestionStats:
    for rec in records:
        try:
            operator = db.scalar(select(Operator).where(Operator.name == rec.operator_name))
            if operator is None:
                operator = Operator(
                    name=rec.operator_name,
                    external_id=None,
                    source_url=rec.source_url,
                    source_metadata={"source_name": rec.source_name},
                )
                db.add(operator)
                db.flush()
                stats.upserted_operators += 1
            else:
                operator.source_url = operator.source_url or rec.source_url
                operator.source_metadata = operator.source_metadata or {"source_name": rec.source_name}

            asset = db.scalar(
                select(Asset).where(
                    and_(
                        Asset.operator_id == operator.id,
                        Asset.name == rec.asset_name,
                        Asset.county == rec.county,
                        Asset.field == rec.field,
                    )
                )
            )
            if asset is None:
                asset = Asset(
                    operator_id=operator.id,
                    name=rec.asset_name,
                    county=rec.county,
                    field=rec.field,
                    basin=rec.basin,
                    status="active",
                    external_id=None,
                    source_url=rec.source_url,
                    source_metadata={"source_name": rec.source_name},
                )
                db.add(asset)
                db.flush()
                stats.upserted_assets += 1

            production = db.scalar(
                select(ProductionRecord).where(
                    and_(
                        ProductionRecord.asset_id == asset.id,
                        ProductionRecord.period_date == rec.period_date,
                    )
                )
            )
            if production is None:
                production = ProductionRecord(
                    asset_id=asset.id,
                    period_date=rec.period_date,
                    oil_bbl=rec.oil_bbl,
                    gas_mcf=rec.gas_mcf,
                    water_bbl=rec.water_bbl,
                    source_url=rec.source_url,
                    source_record_id=rec.source_record_id,
                    source_metadata=rec.source_metadata,
                )
                db.add(production)
                stats.upserted_production_records += 1
            else:
                production.oil_bbl = rec.oil_bbl
                production.gas_mcf = rec.gas_mcf
                production.water_bbl = rec.water_bbl
                production.source_url = rec.source_url
                production.source_record_id = rec.source_record_id
                production.source_metadata = rec.source_metadata
                stats.upserted_production_records += 1
        except Exception as exc:
            stats.partial_failures += 1
            logger.exception("Partial ingestion failure for record", extra={"error": str(exc), "record": rec.source_record_id})

    db.commit()
    return stats
