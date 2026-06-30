"""add archive submission admin upload flag

Revision ID: b3d9a4e2c1f0
Revises: a1f7c5d4c9f2
Create Date: 2026-06-27 17:56:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b3d9a4e2c1f0"
down_revision: Union[str, Sequence[str], None] = "a1f7c5d4c9f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE archive_submissions "
            "ADD COLUMN IF NOT EXISTS is_admin_upload BOOLEAN NOT NULL DEFAULT false"
        )
        return

    op.add_column(
        "archive_submissions",
        sa.Column("is_admin_upload", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE archive_submissions DROP COLUMN IF EXISTS is_admin_upload")
        return

    op.drop_column("archive_submissions", "is_admin_upload")
