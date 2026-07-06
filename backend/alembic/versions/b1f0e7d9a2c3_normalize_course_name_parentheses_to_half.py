"""normalize existing course names to half-width parentheses

Revision ID: b1f0e7d9a2c3
Revises: a8f2d9b6c4e1
Create Date: 2026-07-07 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1f0e7d9a2c3"
down_revision: Union[str, Sequence[str], None] = "a8f2d9b6c4e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLE_COLUMNS = (
    ("courses", "name"),
    ("course_submissions", "name"),
    ("archive_submissions", "subject"),
    ("archive_submissions", "requested_course_name"),
)


def _to_half_paren(sql_expression: str) -> str:
    return f"REPLACE(REPLACE({sql_expression}, '（', '('), '）', ')')"


def _to_full_paren(sql_expression: str) -> str:
    return f"REPLACE(REPLACE({sql_expression}, '(', '（'), ')', '）')"


def _normalize_update(table: str, column: str, to_half: bool = True) -> None:
    transform = _to_half_paren if to_half else _to_full_paren
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
        _normalize_update(table, column, to_half=True)


def downgrade() -> None:
    for table, column in _TABLE_COLUMNS:
        _normalize_update(table, column, to_half=False)
