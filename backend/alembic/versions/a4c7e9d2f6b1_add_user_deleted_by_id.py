"""add user deleted by id

Revision ID: a4c7e9d2f6b1
Revises: d1e6c8a4f2b9
Create Date: 2026-07-22 22:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a4c7e9d2f6b1"
down_revision: Union[str, Sequence[str], None] = "d1e6c8a4f2b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_deleted_by_id_users",
        "users",
        "users",
        ["deleted_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_users_deleted_by_id", "users", ["deleted_by_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_deleted_by_id", table_name="users")
    op.drop_constraint(
        "fk_users_deleted_by_id_users",
        "users",
        type_="foreignkey",
    )
    op.drop_column("users", "deleted_by_id")
