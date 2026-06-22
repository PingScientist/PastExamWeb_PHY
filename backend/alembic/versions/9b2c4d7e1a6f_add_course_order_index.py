"""add_course_order_index

Revision ID: 9b2c4d7e1a6f
Revises: 5f0d3fb0a1c9
Create Date: 2026-06-22 23:18:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9b2c4d7e1a6f"
down_revision: Union[str, Sequence[str], None] = "5f0d3fb0a1c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "courses",
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(op.f("ix_courses_order_index"), "courses", ["order_index"])
    op.alter_column("courses", "order_index", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_courses_order_index"), table_name="courses")
    op.drop_column("courses", "order_index")
