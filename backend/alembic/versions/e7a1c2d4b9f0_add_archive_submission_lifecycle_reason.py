"""add archive submission lifecycle reason

Revision ID: e7a1c2d4b9f0
Revises: b3d9a4e2c1f0, f8d9a7b6c3e2
Create Date: 2026-07-01 20:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e7a1c2d4b9f0"
down_revision: Union[str, Sequence[str], None] = ("b3d9a4e2c1f0", "f8d9a7b6c3e2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE archive_submissions "
            "ADD COLUMN IF NOT EXISTS lifecycle_reason VARCHAR"
        )
        return

    op.add_column(
        "archive_submissions",
        sa.Column("lifecycle_reason", sa.String(), nullable=True),
    )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE archive_submissions DROP COLUMN IF EXISTS lifecycle_reason")
        return

    op.drop_column("archive_submissions", "lifecycle_reason")
