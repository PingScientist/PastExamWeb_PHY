"""add submission review tables

Revision ID: 7c9e2d1f4a8b
Revises: 9b2c4d7e1a6f
Create Date: 2026-06-24 03:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


revision: str = "7c9e2d1f4a8b"
down_revision: Union[str, Sequence[str], None] = "9b2c4d7e1a6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    submissionstatus = sa.Enum(
        "PENDING", "APPROVED", "REJECTED", name="submissionstatus"
    )
    submissionstatus.create(op.get_bind(), checkfirst=True)

    if not inspector.has_table("course_submissions"):
        op.create_table(
            "course_submissions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("category", sa.Enum("FRESHMAN", "SOPHOMORE", "JUNIOR", "SENIOR", "GRADUATE", "INTERDISCIPLINARY", "GENERAL", name="coursecategory", create_type=False), nullable=False),
            sa.Column("status", submissionstatus, nullable=False),
            sa.Column("requester_id", sa.Integer(), nullable=False),
            sa.Column("reviewer_id", sa.Integer(), nullable=True),
            sa.Column("review_note", sa.Text(), nullable=True),
            sa.Column("created_course_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["created_course_id"], ["courses.id"]),
            sa.ForeignKeyConstraint(["requester_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_course_submissions_name"), "course_submissions", ["name"], unique=False)
        op.create_index(op.f("ix_course_submissions_requester_id"), "course_submissions", ["requester_id"], unique=False)
        op.create_index(op.f("ix_course_submissions_status"), "course_submissions", ["status"], unique=False)

    if not inspector.has_table("archive_submissions"):
        op.create_table(
            "archive_submissions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("subject", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("category", sa.Enum("FRESHMAN", "SOPHOMORE", "JUNIOR", "SENIOR", "GRADUATE", "INTERDISCIPLINARY", "GENERAL", name="coursecategory", create_type=False), nullable=False),
            sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("academic_year", sa.Integer(), nullable=False),
            sa.Column("archive_type", sa.Enum("QUIZ", "MIDTERM", "FINAL", "OTHER", name="archivetype", create_type=False), nullable=False),
            sa.Column("professor", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("has_answers", sa.Boolean(), nullable=False),
            sa.Column("object_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column("status", submissionstatus, nullable=False),
            sa.Column("requester_id", sa.Integer(), nullable=False),
            sa.Column("reviewer_id", sa.Integer(), nullable=True),
            sa.Column("review_note", sa.Text(), nullable=True),
            sa.Column("created_archive_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["created_archive_id"], ["archives.id"]),
            sa.ForeignKeyConstraint(["requester_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_archive_submissions_professor"), "archive_submissions", ["professor"], unique=False)
        op.create_index(op.f("ix_archive_submissions_requester_id"), "archive_submissions", ["requester_id"], unique=False)
        op.create_index(op.f("ix_archive_submissions_status"), "archive_submissions", ["status"], unique=False)
        op.create_index(op.f("ix_archive_submissions_subject"), "archive_submissions", ["subject"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_archive_submissions_subject"), table_name="archive_submissions")
    op.drop_index(op.f("ix_archive_submissions_status"), table_name="archive_submissions")
    op.drop_index(op.f("ix_archive_submissions_requester_id"), table_name="archive_submissions")
    op.drop_index(op.f("ix_archive_submissions_professor"), table_name="archive_submissions")
    op.drop_table("archive_submissions")
    op.drop_index(op.f("ix_course_submissions_status"), table_name="course_submissions")
    op.drop_index(op.f("ix_course_submissions_requester_id"), table_name="course_submissions")
    op.drop_index(op.f("ix_course_submissions_name"), table_name="course_submissions")
    op.drop_table("course_submissions")
    sa.Enum(name="submissionstatus").drop(op.get_bind(), checkfirst=True)
