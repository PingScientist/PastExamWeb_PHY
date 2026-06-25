"""add discussion message pin

Revision ID: 7d2e1c9b5a34
Revises: 2f4c8a9d7b11
Create Date: 2026-06-25 22:25:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "7d2e1c9b5a34"
down_revision: Union[str, Sequence[str], None] = "2f4c8a9d7b11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "archive_discussion_messages",
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(
        op.f("ix_archive_discussion_messages_is_pinned"),
        "archive_discussion_messages",
        ["is_pinned"],
        unique=False,
    )
    op.alter_column("archive_discussion_messages", "is_pinned", server_default=None)


def downgrade() -> None:
    op.drop_index(
        op.f("ix_archive_discussion_messages_is_pinned"),
        table_name="archive_discussion_messages",
    )
    op.drop_column("archive_discussion_messages", "is_pinned")
