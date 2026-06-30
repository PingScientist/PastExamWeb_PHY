"""add takedown status to submissionstatus enum

Revision ID: f8d9a7b6c3e2
Revises: d2f6b8c3a9e1
Create Date: 2026-06-28 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f8d9a7b6c3e2"
down_revision: Union[str, Sequence[str], None] = "d2f6b8c3a9e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TYPE submissionstatus ADD VALUE IF NOT EXISTS 'TAKEDOWN'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values directly in-place.
    # Keep this migration forward-safe and use a separate migration for full replacement if needed.
    pass
