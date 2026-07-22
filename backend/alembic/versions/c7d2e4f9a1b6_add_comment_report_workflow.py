"""add comment report workflow

Revision ID: c7d2e4f9a1b6
Revises: 8a1c4d7e2f90
Create Date: 2026-07-20 06:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c7d2e4f9a1b6"
down_revision: Union[str, Sequence[str], None] = "8a1c4d7e2f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comment_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporter_user_id", sa.Integer(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.Column("comment_author_id", sa.Integer(), nullable=True),
        sa.Column("archive_id", sa.Integer(), nullable=True),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("thread_id", sa.Integer(), nullable=True),
        sa.Column("reply_to_message_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.String(length=50), nullable=False),
        sa.Column("custom_message", sa.Text(), nullable=True),
        sa.Column("comment_content_snapshot", sa.Text(), nullable=False),
        sa.Column("comment_author_name_snapshot", sa.String(length=100), nullable=False),
        sa.Column("comment_created_at_snapshot", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archive_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("course_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("admin_response", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "comment_deleted", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["archive_id"], ["archives.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["comment_author_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"], ["archive_discussion_messages.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["reporter_user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "reporter_user_id",
        "comment_id",
        "comment_author_id",
        "archive_id",
        "course_id",
        "thread_id",
        "reason",
        "status",
        "reviewed_by",
        "reviewed_at",
        "created_at",
    ):
        op.create_index(
            op.f(f"ix_comment_reports_{column}"),
            "comment_reports",
            [column],
            unique=False,
        )
    op.create_index(
        "ix_comment_reports_status_created",
        "comment_reports",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "uq_comment_reports_active_reporter_comment_reason",
        "comment_reports",
        ["reporter_user_id", "comment_id", "reason"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'in_review')"),
    )


def downgrade() -> None:
    op.drop_table("comment_reports")
