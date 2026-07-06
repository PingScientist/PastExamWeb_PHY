"""normalize existing course names to full-width parentheses

Revision ID: a8f2d9b6c4e1
Revises: bf2c9d7a8e4f
Create Date: 2026-07-07 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8f2d9b6c4e1"
down_revision: Union[str, Sequence[str], None] = "bf2c9d7a8e4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLE_COLUMNS = (
    ("courses", "name"),
    ("course_submissions", "name"),
    ("archive_submissions", "subject"),
    ("archive_submissions", "requested_course_name"),
)


def _to_full_paren(sql_expression: str) -> str:
    return f"REPLACE(REPLACE({sql_expression}, '(', '（'), ')', '）')"


def _to_half_paren(sql_expression: str) -> str:
    return f"REPLACE(REPLACE({sql_expression}, '（', '('), '）', ')')"


def _normalize_update(table: str, column: str, to_full: bool = True) -> None:
    transform = _to_full_paren if to_full else _to_half_paren
    transformed_value = transform(f'"{column}"')
    original_value = f'"{column}"'
    op.execute(
        sa.text(
            f"""
            UPDATE "{table}"
            SET {column} = {transformed_value}
            WHERE {original_value} IS NOT NULL
              AND {original_value} <> {transformed_value}
            """
        )
    )


def upgrade() -> None:
    for table, column in _TABLE_COLUMNS:
        _normalize_update(table, column, to_full=True)


def downgrade() -> None:
    for table, column in _TABLE_COLUMNS:
        _normalize_update(table, column, to_full=False)
