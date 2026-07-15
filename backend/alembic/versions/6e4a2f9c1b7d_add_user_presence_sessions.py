"""add user presence sessions

Revision ID: 6e4a2f9c1b7d
Revises: f2a4c6e8b1d3
Create Date: 2026-07-13 01:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6e4a2f9c1b7d"
down_revision: Union[str, Sequence[str], None] = "f2a4c6e8b1d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_presence_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_identifier", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_presence_sessions_user_started",
        "user_presence_sessions",
        ["user_id", "started_at"],
    )
    op.create_index(
        "ix_user_presence_sessions_identifier",
        "user_presence_sessions",
        ["session_identifier"],
    )
    op.create_index(
        "ix_user_presence_sessions_last_seen",
        "user_presence_sessions",
        ["last_seen_at"],
    )
    op.create_index(
        "ix_user_presence_sessions_ended",
        "user_presence_sessions",
        ["ended_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_presence_sessions_ended", table_name="user_presence_sessions"
    )
    op.drop_index(
        "ix_user_presence_sessions_last_seen", table_name="user_presence_sessions"
    )
    op.drop_index(
        "ix_user_presence_sessions_identifier", table_name="user_presence_sessions"
    )
    op.drop_index(
        "ix_user_presence_sessions_user_started", table_name="user_presence_sessions"
    )
    op.drop_table("user_presence_sessions")
