"""add archive submission course request fields

Revision ID: 2f4c8a9d7b11
Revises: b6f1e2d9a4c7
Create Date: 2026-06-25 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2f4c8a9d7b11"
down_revision: Union[str, None] = "b6f1e2d9a4c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "archive_submissions",
        sa.Column("requested_course_name", sa.String(), nullable=True),
    )
    op.add_column(
        "archive_submissions",
        sa.Column("requested_category_key", sa.String(), nullable=True),
    )
    op.add_column(
        "archive_submissions",
        sa.Column("requested_category_name", sa.String(), nullable=True),
    )
    op.add_column(
        "archive_submissions",
        sa.Column("requested_category_label", sa.String(), nullable=True),
    )
    op.add_column(
        "archive_submissions",
        sa.Column("requested_category_icon", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("archive_submissions", "requested_category_icon")
    op.drop_column("archive_submissions", "requested_category_label")
    op.drop_column("archive_submissions", "requested_category_name")
    op.drop_column("archive_submissions", "requested_category_key")
    op.drop_column("archive_submissions", "requested_course_name")
