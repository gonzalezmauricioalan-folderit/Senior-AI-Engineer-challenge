"""View clean_activity_events: activity_events minus exact duplicates (lowest id kept).

Portable SQL (Postgres and SQLite); NULLs fall in the same partition on both engines.

Revision ID: 0002_clean_activity_events
Revises: 0001_initial_schema
Create Date: 2026-11-03
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_clean_activity_events"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE VIEW clean_activity_events AS
        SELECT id, account_id, location, event_type, occurred_at, duration_seconds, outcome
        FROM (
          SELECT e.*, ROW_NUMBER() OVER (
            PARTITION BY account_id, location, event_type, occurred_at, duration_seconds, outcome
            ORDER BY id) AS rn
          FROM activity_events e
        ) t
        WHERE rn = 1
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW clean_activity_events")
