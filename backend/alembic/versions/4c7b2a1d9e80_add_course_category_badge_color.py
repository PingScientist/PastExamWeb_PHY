"""add course category badge color

Revision ID: 4c7b2a1d9e80
Revises: e7a1c2d4b9f0
Create Date: 2026-07-04 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "4c7b2a1d9e80"
down_revision: Union[str, Sequence[str], None] = "e7a1c2d4b9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "course_category_configs",
        sa.Column("badge_color", sa.String(), nullable=False, server_default="blue"),
    )


def downgrade() -> None:
    op.drop_column("course_category_configs", "badge_color")
