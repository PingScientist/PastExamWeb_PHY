"""add last_seen_at to users

Revision ID: bf2c9d7a8e4f
Revises: 4c7b2a1d9e80
Create Date: 2026-07-04 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bf2c9d7a8e4f"
down_revision: Union[str, Sequence[str], None] = "4c7b2a1d9e80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "last_seen_at")
