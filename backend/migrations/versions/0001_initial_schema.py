"""Initial schema: accounts and activity_events (from the starter schema.sql).

Timestamps are `timestamp without time zone` and hold UTC values; convert to the
account's IANA timezone at query time. IDs are plain integers (no sequence)
because the seed supplies explicit ids.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("industry", sa.String(60), nullable=False),
        sa.Column("timezone", sa.String(60), nullable=False, comment="IANA timezone, e.g. America/Chicago"),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, comment="UTC"),
    )
    op.create_table(
        "activity_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("location", sa.String(80), nullable=False, comment="Site/branch; unique only within an account"),
        sa.Column("event_type", sa.String(40), nullable=False, comment="call_received | lead_created | appointment_set"),
        sa.Column("occurred_at", sa.DateTime(timezone=False), nullable=False, comment="UTC"),
        sa.Column("duration_seconds", sa.Integer, nullable=True, comment="Calls only; may be NULL"),
        sa.Column("outcome", sa.String(40), nullable=True, comment="May be NULL"),
    )
    # Covers the FK and the main access pattern (one account, a time range).
    op.create_index(
        "ix_activity_events_account_id_occurred_at",
        "activity_events",
        ["account_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_activity_events_account_id_occurred_at", table_name="activity_events")
    op.drop_table("activity_events")
    op.drop_table("accounts")
