"""add ingestion traceability columns

Revision ID: 0002_ingestion_traceability
Revises: 0001_init
Create Date: 2026-03-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_ingestion_traceability"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("operators", sa.Column("external_id", sa.String(length=100), nullable=True))
    op.add_column("operators", sa.Column("source_url", sa.Text(), nullable=True))
    op.add_column("operators", sa.Column("source_metadata", sa.JSON(), nullable=True))

    op.add_column("assets", sa.Column("external_id", sa.String(length=100), nullable=True))
    op.add_column("assets", sa.Column("source_url", sa.Text(), nullable=True))
    op.add_column("assets", sa.Column("source_metadata", sa.JSON(), nullable=True))

    op.add_column("production_records", sa.Column("source_url", sa.Text(), nullable=True))
    op.add_column("production_records", sa.Column("source_record_id", sa.String(length=120), nullable=True))
    op.add_column("production_records", sa.Column("source_metadata", sa.JSON(), nullable=True))

    op.create_unique_constraint("uq_production_asset_period", "production_records", ["asset_id", "period_date"])


def downgrade() -> None:
    op.drop_constraint("uq_production_asset_period", "production_records", type_="unique")

    op.drop_column("production_records", "source_metadata")
    op.drop_column("production_records", "source_record_id")
    op.drop_column("production_records", "source_url")

    op.drop_column("assets", "source_metadata")
    op.drop_column("assets", "source_url")
    op.drop_column("assets", "external_id")

    op.drop_column("operators", "source_metadata")
    op.drop_column("operators", "source_url")
    op.drop_column("operators", "external_id")
