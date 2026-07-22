"""simplify comment report status

Revision ID: a5c7e9f2d4b6
Revises: f4a6c8e1b2d3
Create Date: 2026-07-22 12:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a5c7e9f2d4b6"
down_revision: Union[str, Sequence[str], None] = "f4a6c8e1b2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE comment_reports SET status = 'pending' "
            "WHERE status = 'in_review'"
        )
    )
    op.drop_index(
        "uq_comment_reports_active_reporter_comment_reason",
        table_name="comment_reports",
    )
    op.create_index(
        "uq_comment_reports_active_reporter_comment_reason",
        "comment_reports",
        ["reporter_user_id", "comment_id", "reason"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_check_constraint(
        "ck_comment_reports_status",
        "comment_reports",
        "status IN ('pending', 'upheld', 'dismissed')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_comment_reports_status",
        "comment_reports",
        type_="check",
    )
    op.drop_index(
        "uq_comment_reports_active_reporter_comment_reason",
        table_name="comment_reports",
    )
    op.create_index(
        "uq_comment_reports_active_reporter_comment_reason",
        "comment_reports",
        ["reporter_user_id", "comment_id", "reason"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'in_review')"),
    )
