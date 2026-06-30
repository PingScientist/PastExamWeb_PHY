"""add archive deleted by id

Revision ID: d2f6b8c3a9e1
Revises: c6e8f2a9d4b1
Create Date: 2026-06-27 18:05:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d2f6b8c3a9e1"
down_revision: Union[str, Sequence[str], None] = "c6e8f2a9d4b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("archives", sa.Column("deleted_by_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("archives", "deleted_by_id")
