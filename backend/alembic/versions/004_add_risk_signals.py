"""Add RiskSense risk signals

Revision ID: 004
Revises: 003
Create Date: 2026-05-17 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_clause_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_id", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("LOW", "MEDIUM", "HIGH", name="riskseverity"),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["source_clause_id"], ["clauses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_risk_signals_document_id"),
        "risk_signals",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_risk_signals_source_clause_id"),
        "risk_signals",
        ["source_clause_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_risk_signals_source_clause_id"), table_name="risk_signals")
    op.drop_index(op.f("ix_risk_signals_document_id"), table_name="risk_signals")
    op.drop_table("risk_signals")
