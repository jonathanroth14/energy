"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2026-03-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "operators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("headquarters", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "court_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("debtor_name", sa.String(length=255), nullable=False),
        sa.Column("chapter", sa.String(length=20), nullable=False),
        sa.Column("court_name", sa.String(length=255), nullable=False),
        sa.Column("filed_date", sa.Date(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
    )
    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("operator_id", sa.Integer(), sa.ForeignKey("operators.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("county", sa.String(length=100), nullable=False),
        sa.Column("field", sa.String(length=100), nullable=False),
        sa.Column("basin", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "docket_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("court_case_id", sa.Integer(), sa.ForeignKey("court_cases.id"), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
    )
    op.create_table(
        "production_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("period_date", sa.Date(), nullable=False),
        sa.Column("oil_bbl", sa.Float(), nullable=False),
        sa.Column("gas_mcf", sa.Float(), nullable=False),
        sa.Column("water_bbl", sa.Float(), nullable=False),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=True),
        sa.Column("court_case_id", sa.Integer(), sa.ForeignKey("court_cases.id"), nullable=True),
        sa.Column("signal_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("why_fired", sa.Text(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("watchlist_id", sa.Integer(), sa.ForeignKey("watchlists.id"), nullable=False),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("watchlist_items")
    op.drop_table("alerts")
    op.drop_table("production_records")
    op.drop_table("docket_entries")
    op.drop_table("assets")
    op.drop_table("watchlists")
    op.drop_table("court_cases")
    op.drop_table("operators")
