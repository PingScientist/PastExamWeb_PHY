"""add report trash metadata

Revision ID: f4a6c8e1b2d3
Revises: e9c3a1b7d5f2
Create Date: 2026-07-22 05:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f4a6c8e1b2d3"
down_revision: Union[str, Sequence[str], None] = "e9c3a1b7d5f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table_name in ("system_issue_reports", "comment_reports"):
        op.add_column(
            table_name,
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.add_column(
            table_name,
            sa.Column("deleted_by_id", sa.Integer(), nullable=True),
        )
        op.create_index(
            op.f(f"ix_{table_name}_deleted_at"),
            table_name,
            ["deleted_at"],
            unique=False,
        )
        op.create_index(
            op.f(f"ix_{table_name}_deleted_by_id"),
            table_name,
            ["deleted_by_id"],
            unique=False,
        )
        op.create_foreign_key(
            f"fk_{table_name}_deleted_by_id_users",
            table_name,
            "users",
            ["deleted_by_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    for table_name in ("comment_reports", "system_issue_reports"):
        op.drop_constraint(
            f"fk_{table_name}_deleted_by_id_users",
            table_name,
            type_="foreignkey",
        )
        op.drop_index(op.f(f"ix_{table_name}_deleted_by_id"), table_name=table_name)
        op.drop_index(op.f(f"ix_{table_name}_deleted_at"), table_name=table_name)
        op.drop_column(table_name, "deleted_by_id")
        op.drop_column(table_name, "deleted_at")
