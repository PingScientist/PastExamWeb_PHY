"""add discussion threads and likes

Revision ID: 5b8d2f1c9a47
Revises: 3a7e9c1d5b42
Create Date: 2026-07-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "5b8d2f1c9a47"
down_revision: Union[str, Sequence[str], None] = "3a7e9c1d5b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "archive_discussion_messages",
        sa.Column("parent_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "archive_discussion_messages",
        sa.Column("reply_to_message_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_archive_discussion_messages_parent_id",
        "archive_discussion_messages",
        "archive_discussion_messages",
        ["parent_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_archive_discussion_messages_reply_to_message_id",
        "archive_discussion_messages",
        "archive_discussion_messages",
        ["reply_to_message_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_archive_discussion_messages_parent_id"),
        "archive_discussion_messages",
        ["parent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_archive_discussion_messages_reply_to_message_id"),
        "archive_discussion_messages",
        ["reply_to_message_id"],
        unique=False,
    )
    op.create_index(
        "ix_archive_discussion_messages_archive_parent",
        "archive_discussion_messages",
        ["archive_id", "parent_id"],
        unique=False,
    )

    op.create_table(
        "archive_discussion_likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["archive_discussion_messages.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "message_id",
            "user_id",
            name="uq_archive_discussion_likes_message_user",
        ),
    )
    op.create_index(
        op.f("ix_archive_discussion_likes_message_id"),
        "archive_discussion_likes",
        ["message_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_archive_discussion_likes_user_id"),
        "archive_discussion_likes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_archive_discussion_likes_user_id"),
        table_name="archive_discussion_likes",
    )
    op.drop_index(
        op.f("ix_archive_discussion_likes_message_id"),
        table_name="archive_discussion_likes",
    )
    op.drop_table("archive_discussion_likes")

    op.drop_index(
        "ix_archive_discussion_messages_archive_parent",
        table_name="archive_discussion_messages",
    )
    op.drop_index(
        op.f("ix_archive_discussion_messages_reply_to_message_id"),
        table_name="archive_discussion_messages",
    )
    op.drop_index(
        op.f("ix_archive_discussion_messages_parent_id"),
        table_name="archive_discussion_messages",
    )
    op.drop_constraint(
        "fk_archive_discussion_messages_reply_to_message_id",
        "archive_discussion_messages",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_archive_discussion_messages_parent_id",
        "archive_discussion_messages",
        type_="foreignkey",
    )
    op.drop_column("archive_discussion_messages", "reply_to_message_id")
    op.drop_column("archive_discussion_messages", "parent_id")
