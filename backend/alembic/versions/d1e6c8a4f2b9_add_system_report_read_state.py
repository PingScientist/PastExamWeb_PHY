"""add system report read state

Revision ID: d1e6c8a4f2b9
Revises: b8d1f3a6c9e2
Create Date: 2026-07-22 21:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d1e6c8a4f2b9"
down_revision: Union[str, Sequence[str], None] = "b8d1f3a6c9e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "system_issue_reports",
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "system_issue_reports",
        sa.Column("read_by_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_system_issue_reports_read_by_user_id_users",
        "system_issue_reports",
        "users",
        ["read_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_system_issue_reports_read_at_created",
        "system_issue_reports",
        ["read_at", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_system_issue_reports_read_at_created",
        table_name="system_issue_reports",
    )
    op.drop_constraint(
        "fk_system_issue_reports_read_by_user_id_users",
        "system_issue_reports",
        type_="foreignkey",
    )
    op.drop_column("system_issue_reports", "read_by_user_id")
    op.drop_column("system_issue_reports", "read_at")
