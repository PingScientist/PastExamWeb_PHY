"""add announcement reads and personal notifications

Revision ID: 8a1c4d7e2f90
Revises: 5b8d2f1c9a47
Create Date: 2026-07-20 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "8a1c4d7e2f90"
down_revision: Union[str, Sequence[str], None] = "5b8d2f1c9a47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "announcement_read_receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("notification_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["notification_id"], ["notifications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "notification_id",
            "user_id",
            name="uq_announcement_read_receipts_notification_user",
        ),
    )
    op.create_index(
        op.f("ix_announcement_read_receipts_notification_id"),
        "announcement_read_receipts",
        ["notification_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_announcement_read_receipts_user_id"),
        "announcement_read_receipts",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_announcement_read_receipts_read_at"),
        "announcement_read_receipts",
        ["read_at"],
        unique=False,
    )
    op.create_index(
        "ix_announcement_read_receipts_user_read",
        "announcement_read_receipts",
        ["user_id", "read_at"],
        unique=False,
    )

    op.create_table(
        "personal_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("source_message_id", sa.Integer(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("dedupe_key", sa.String(length=160), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_message_id"],
            ["archive_discussion_messages.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dedupe_key", name="uq_personal_notifications_dedupe_key"),
    )
    for column in (
        "user_id",
        "notification_type",
        "source_type",
        "source_id",
        "source_message_id",
        "read_at",
        "created_at",
    ):
        op.create_index(
            op.f(f"ix_personal_notifications_{column}"),
            "personal_notifications",
            [column],
            unique=False,
        )
    op.create_index(
        "ix_personal_notifications_user_read_created",
        "personal_notifications",
        ["user_id", "read_at", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_personal_notifications_user_read_created",
        table_name="personal_notifications",
    )
    for column in reversed(
        (
            "user_id",
            "notification_type",
            "source_type",
            "source_id",
            "source_message_id",
            "read_at",
            "created_at",
        )
    ):
        op.drop_index(
            op.f(f"ix_personal_notifications_{column}"),
            table_name="personal_notifications",
        )
    op.drop_table("personal_notifications")

    op.drop_index(
        "ix_announcement_read_receipts_user_read",
        table_name="announcement_read_receipts",
    )
    op.drop_index(
        op.f("ix_announcement_read_receipts_read_at"),
        table_name="announcement_read_receipts",
    )
    op.drop_index(
        op.f("ix_announcement_read_receipts_user_id"),
        table_name="announcement_read_receipts",
    )
    op.drop_index(
        op.f("ix_announcement_read_receipts_notification_id"),
        table_name="announcement_read_receipts",
    )
    op.drop_table("announcement_read_receipts")
