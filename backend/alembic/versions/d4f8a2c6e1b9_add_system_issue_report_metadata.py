"""add system issue report metadata

Revision ID: d4f8a2c6e1b9
Revises: c7d2e4f9a1b6
Create Date: 2026-07-20 06:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d4f8a2c6e1b9"
down_revision: Union[str, Sequence[str], None] = "c7d2e4f9a1b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_issue_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporter_user_id", sa.Integer(), nullable=True),
        sa.Column("report_type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("contact", sa.String(length=200), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'local_only'"),
            nullable=False,
        ),
        sa.Column("github_issue_number", sa.Integer(), nullable=True),
        sa.Column("github_issue_url", sa.String(length=500), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["reporter_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "reporter_user_id",
        "report_type",
        "status",
        "github_issue_number",
        "created_at",
    ):
        op.create_index(
            op.f(f"ix_system_issue_reports_{column}"),
            "system_issue_reports",
            [column],
            unique=False,
        )
    op.create_index(
        "ix_system_issue_reports_status_created",
        "system_issue_reports",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("system_issue_reports")
