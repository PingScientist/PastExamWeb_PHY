"""add trash metadata columns

Revision ID: a1f7c5d4c9f2
Revises: 7d2e1c9b5a34
Create Date: 2026-06-27 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1f7c5d4c9f2"
down_revision: Union[str, Sequence[str], None] = "7d2e1c9b5a34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE submissionstatus ADD VALUE IF NOT EXISTS 'DELETED'")

    op.add_column(
        "course_category_configs",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "course_category_configs",
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "course_category_configs",
        sa.Column("restored_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "course_category_configs",
        sa.Column("restored_by_id", sa.Integer(), nullable=True),
    )

    op.add_column("courses", sa.Column("deleted_by_id", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("restored_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("courses", sa.Column("restored_by_id", sa.Integer(), nullable=True))

    op.add_column("archives", sa.Column("deleted_reason", sa.Text(), nullable=True))
    op.add_column("archives", sa.Column("restored_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("archives", sa.Column("restored_by_id", sa.Integer(), nullable=True))

    op.add_column("archive_submissions", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.add_column("archive_submissions", sa.Column("deleted_by_id", sa.Integer(), nullable=True))
    op.add_column("archive_submissions", sa.Column("delete_reason", sa.Text(), nullable=True))
    op.add_column("archive_submissions", sa.Column("restored_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("archive_submissions", sa.Column("restored_by_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("archive_submissions", "restored_by_id")
    op.drop_column("archive_submissions", "restored_at")
    op.drop_column("archive_submissions", "delete_reason")
    op.drop_column("archive_submissions", "deleted_by_id")
    op.drop_column("archive_submissions", "owner_id")

    op.drop_column("archives", "restored_by_id")
    op.drop_column("archives", "restored_at")
    op.drop_column("archives", "deleted_reason")

    op.drop_column("courses", "restored_by_id")
    op.drop_column("courses", "restored_at")
    op.drop_column("courses", "deleted_by_id")

    op.drop_column("course_category_configs", "restored_by_id")
    op.drop_column("course_category_configs", "restored_at")
    op.drop_column("course_category_configs", "deleted_by_id")
    op.drop_column("course_category_configs", "deleted_at")
