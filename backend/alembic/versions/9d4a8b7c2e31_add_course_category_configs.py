"""add course category configs

Revision ID: 9d4a8b7c2e31
Revises: 7c9e2d1f4a8b
Create Date: 2026-06-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d4a8b7c2e31"
down_revision: Union[str, None] = "7c9e2d1f4a8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_CATEGORIES = [
    ("freshman", "基礎必修", "基礎", "pi pi-fw pi-book", 0),
    ("sophomore", "專業必修", "必修", "pi pi-fw pi-compass", 1),
    ("junior", "實驗課程", "實驗", "pi pi-fw pi-sparkles", 2),
    ("senior", "專業選修", "選修", "pi pi-fw pi-book", 3),
    ("graduate", "研究所", "研究所", "pi pi-fw pi-graduation-cap", 4),
    ("interdisciplinary", "戳戳數學系", "數學", "pi pi-fw pi-calculator", 5),
]


def _enum_to_string(table_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"]: column for column in inspector.get_columns(table_name)}
    if "category" not in columns:
        return
    if isinstance(columns["category"]["type"], sa.String):
        return
    op.execute(
        sa.text(
            f"ALTER TABLE {table_name} ALTER COLUMN category TYPE VARCHAR "
            "USING lower(category::text)"
        )
    )


def upgrade() -> None:
    op.create_table(
        "course_category_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False, server_default=""),
        sa.Column("icon", sa.String(), nullable=False, server_default="pi pi-fw pi-book"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_course_category_configs_key"), "course_category_configs", ["key"], unique=True)
    op.create_index(op.f("ix_course_category_configs_name"), "course_category_configs", ["name"], unique=False)
    op.create_index(op.f("ix_course_category_configs_order_index"), "course_category_configs", ["order_index"], unique=False)
    op.create_index(op.f("ix_course_category_configs_is_active"), "course_category_configs", ["is_active"], unique=False)

    category_table = sa.table(
        "course_category_configs",
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("label", sa.String),
        sa.column("icon", sa.String),
        sa.column("order_index", sa.Integer),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        category_table,
        [
            {
                "key": key,
                "name": name,
                "label": label,
                "icon": icon,
                "order_index": order_index,
                "is_active": True,
            }
            for key, name, label, icon, order_index in DEFAULT_CATEGORIES
        ],
    )

    for table_name in ("courses", "course_submissions", "archive_submissions"):
        _enum_to_string(table_name)


def downgrade() -> None:
    op.drop_index(op.f("ix_course_category_configs_is_active"), table_name="course_category_configs")
    op.drop_index(op.f("ix_course_category_configs_order_index"), table_name="course_category_configs")
    op.drop_index(op.f("ix_course_category_configs_name"), table_name="course_category_configs")
    op.drop_index(op.f("ix_course_category_configs_key"), table_name="course_category_configs")
    op.drop_table("course_category_configs")
