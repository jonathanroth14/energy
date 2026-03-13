"""add bankruptcy traceability fields

Revision ID: 0003_bankruptcy_traceability
Revises: 0002_ingestion_traceability
Create Date: 2026-03-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_bankruptcy_traceability"
down_revision = "0002_ingestion_traceability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("court_cases", sa.Column("external_case_id", sa.String(length=100), nullable=True))
    op.add_column("court_cases", sa.Column("source_provider", sa.String(length=50), nullable=True))
    op.add_column("court_cases", sa.Column("source_metadata", sa.JSON(), nullable=True))
    op.create_unique_constraint("uq_court_cases_external_case_id", "court_cases", ["external_case_id"])

    op.add_column("docket_entries", sa.Column("external_docket_id", sa.String(length=120), nullable=True))
    op.add_column("docket_entries", sa.Column("source_provider", sa.String(length=50), nullable=True))
    op.add_column("docket_entries", sa.Column("source_metadata", sa.JSON(), nullable=True))
    op.create_unique_constraint("uq_docket_entries_external_docket_id", "docket_entries", ["external_docket_id"])


def downgrade() -> None:
    op.drop_constraint("uq_docket_entries_external_docket_id", "docket_entries", type_="unique")
    op.drop_column("docket_entries", "source_metadata")
    op.drop_column("docket_entries", "source_provider")
    op.drop_column("docket_entries", "external_docket_id")

    op.drop_constraint("uq_court_cases_external_case_id", "court_cases", type_="unique")
    op.drop_column("court_cases", "source_metadata")
    op.drop_column("court_cases", "source_provider")
    op.drop_column("court_cases", "external_case_id")
