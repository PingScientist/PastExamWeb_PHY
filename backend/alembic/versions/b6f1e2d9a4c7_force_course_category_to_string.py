"""force course category columns to string

Revision ID: b6f1e2d9a4c7
Revises: 9d4a8b7c2e31
Create Date: 2026-06-25 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "b6f1e2d9a4c7"
down_revision: Union[str, None] = "9d4a8b7c2e31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table_name in ("courses", "course_submissions", "archive_submissions"):
        op.execute(
            f"ALTER TABLE {table_name} ALTER COLUMN category TYPE VARCHAR "
            "USING lower(category::text)"
        )


def downgrade() -> None:
    # Intentionally keep category columns as strings. Dynamic admin-managed
    # categories cannot be represented by the old static enum safely.
    pass
