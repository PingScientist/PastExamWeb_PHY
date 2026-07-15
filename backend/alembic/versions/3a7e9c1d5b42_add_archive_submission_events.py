"""add archive submission events

Revision ID: 3a7e9c1d5b42
Revises: 6e4a2f9c1b7d
Create Date: 2026-07-15 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3a7e9c1d5b42"
down_revision: Union[str, Sequence[str], None] = "6e4a2f9c1b7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "archive_submission_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_archive_submission_events_submission_id",
        "archive_submission_events",
        ["submission_id"],
        unique=True,
    )
    op.create_index(
        "ix_archive_submission_events_submitted_at",
        "archive_submission_events",
        ["submitted_at"],
        unique=False,
    )
    op.execute(
        """
        INSERT INTO archive_submission_events (submission_id, submitted_at)
        SELECT id, created_at
        FROM archive_submissions
        ON CONFLICT (submission_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_archive_submission_events_submitted_at",
        table_name="archive_submission_events",
    )
    op.drop_index(
        "ix_archive_submission_events_submission_id",
        table_name="archive_submission_events",
    )
    op.drop_table("archive_submission_events")
