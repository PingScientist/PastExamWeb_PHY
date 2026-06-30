"""add archive submission deleted at

Revision ID: c6e8f2a9d4b1
Revises: a1f7c5d4c9f2
Create Date: 2026-06-27 17:57:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c6e8f2a9d4b1"
down_revision: Union[str, Sequence[str], None] = "a1f7c5d4c9f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "archive_submissions",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("archive_submissions", "deleted_at")
