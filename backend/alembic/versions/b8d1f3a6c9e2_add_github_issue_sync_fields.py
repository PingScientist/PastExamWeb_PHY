"""add github issue sync fields

Revision ID: b8d1f3a6c9e2
Revises: a5c7e9f2d4b6
Create Date: 2026-07-22 13:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b8d1f3a6c9e2"
down_revision: Union[str, Sequence[str], None] = "a5c7e9f2d4b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "system_issue_reports",
        sa.Column("github_issue_state", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "system_issue_reports",
        sa.Column("github_linked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "system_issue_reports",
        sa.Column(
            "github_sync_status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
    )
    op.add_column(
        "system_issue_reports",
        sa.Column("github_sync_error", sa.String(length=300), nullable=True),
    )
    op.create_index(
        op.f("ix_system_issue_reports_github_sync_status"),
        "system_issue_reports",
        ["github_sync_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_system_issue_reports_github_sync_status"),
        table_name="system_issue_reports",
    )
    op.drop_column("system_issue_reports", "github_sync_error")
    op.drop_column("system_issue_reports", "github_sync_status")
    op.drop_column("system_issue_reports", "github_linked_at")
    op.drop_column("system_issue_reports", "github_issue_state")
