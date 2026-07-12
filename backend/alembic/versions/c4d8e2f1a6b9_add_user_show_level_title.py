"""add user show level title preference

Revision ID: c4d8e2f1a6b9
Revises: b1f0e7d9a2c3
Create Date: 2026-07-12 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c4d8e2f1a6b9"
down_revision: Union[str, Sequence[str], None] = "b1f0e7d9a2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "show_level_title",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "show_level_title")
