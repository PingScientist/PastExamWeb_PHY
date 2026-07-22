"""add notification actor fields

Revision ID: e9c3a1b7d5f2
Revises: d4f8a2c6e1b9
Create Date: 2026-07-22 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e9c3a1b7d5f2"
down_revision: Union[str, Sequence[str], None] = "d4f8a2c6e1b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notifications", sa.Column("updated_by_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "notifications", sa.Column("deleted_by_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_notifications_updated_by_id_users",
        "notifications",
        "users",
        ["updated_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_notifications_deleted_by_id_users",
        "notifications",
        "users",
        ["deleted_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_notifications_updated_by_id",
        "notifications",
        ["updated_by_id"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_deleted_by_id",
        "notifications",
        ["deleted_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_deleted_by_id", table_name="notifications")
    op.drop_index("ix_notifications_updated_by_id", table_name="notifications")
    op.drop_constraint(
        "fk_notifications_deleted_by_id_users", "notifications", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_notifications_updated_by_id_users", "notifications", type_="foreignkey"
    )
    op.drop_column("notifications", "deleted_by_id")
    op.drop_column("notifications", "updated_by_id")
