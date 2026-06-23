from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String, Text
from sqlmodel import Field, Relationship, SQLModel


class CourseCategory(str, PyEnum):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    GRADUATE = "graduate"
    INTERDISCIPLINARY = "interdisciplinary"
    GENERAL = "general"


class ArchiveType(str, PyEnum):
    QUIZ = "quiz"
    MIDTERM = "midterm"
    FINAL = "final"
    OTHER = "other"


class NotificationSeverity(str, PyEnum):
    INFO = "info"
    DANGER = "danger"


class SubmissionStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    oauth_provider: Optional[str] = Field(default=None)
    oauth_sub: Optional[str] = Field(default=None)
    email: str = Field(unique=True, index=True)
    name: str = Field(unique=True, index=True)
    nickname: Optional[str] = Field(default=None, index=True)
    is_admin: bool = Field(default=False)
    password_hash: Optional[str] = Field(default=None)
    is_local: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    last_login: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    last_logout: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    archives: List["Archive"] = Relationship(back_populates="uploader")


class Course(SQLModel, table=True):
    __tablename__ = "courses"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    category: CourseCategory
    order_index: int = Field(default=0, index=True)
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    archives: List["Archive"] = Relationship(back_populates="course")


class Archive(SQLModel, table=True):
    __tablename__ = "archives"
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    academic_year: int
    archive_type: ArchiveType
    professor: str = Field(index=True)
    has_answers: bool = False
    download_count: int = Field(default=0)

    object_name: str

    uploader_id: Optional[int] = Field(default=None, foreign_key="users.id")
    uploader: Optional["User"] = Relationship(back_populates="archives")

    course_id: int = Field(foreign_key="courses.id")
    course: "Course" = Relationship(back_populates="archives")

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class CourseSubmission(SQLModel, table=True):
    __tablename__ = "course_submissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    category: CourseCategory
    status: SubmissionStatus = Field(default=SubmissionStatus.PENDING, index=True)
    requester_id: int = Field(foreign_key="users.id", index=True)
    reviewer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    review_note: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_course_id: Optional[int] = Field(default=None, foreign_key="courses.id")
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )
    reviewed_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class ArchiveSubmission(SQLModel, table=True):
    __tablename__ = "archive_submissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str = Field(index=True)
    category: CourseCategory
    name: str
    academic_year: int
    archive_type: ArchiveType
    professor: str = Field(index=True)
    has_answers: bool = False
    object_name: str
    status: SubmissionStatus = Field(default=SubmissionStatus.PENDING, index=True)
    requester_id: int = Field(foreign_key="users.id", index=True)
    reviewer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    review_note: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_archive_id: Optional[int] = Field(default=None, foreign_key="archives.id")
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )
    reviewed_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class ArchiveDiscussionMessage(SQLModel, table=True):
    __tablename__ = "archive_discussion_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    archive_id: int = Field(foreign_key="archives.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )


class Meme(SQLModel, table=True):
    __tablename__ = "memes"
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    language: str


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(150), nullable=False))
    body: str = Field(sa_column=Column(Text, nullable=False))
    severity: NotificationSeverity = Field(default=NotificationSeverity.INFO)
    is_active: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    starts_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    ends_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
    )


class UserRead(BaseModel):
    id: int
    email: str
    name: str
    nickname: Optional[str] = None
    is_admin: bool
    is_local: bool
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


class UserNicknameUpdate(BaseModel):
    nickname: str


class UserRoles(BaseModel):
    user_id: int
    is_admin: bool = False

    class Config:
        from_attributes = True


class MemeRead(BaseModel):
    id: int
    content: str
    language: str

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    title: str
    body: str
    severity: NotificationSeverity = NotificationSeverity.INFO
    is_active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    severity: Optional[NotificationSeverity] = None
    is_active: Optional[bool] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class NotificationRead(NotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseInfo(BaseModel):
    id: int
    name: str
    order_index: int = 0

    class Config:
        from_attributes = True


class CoursesByCategory(BaseModel):
    freshman: List[CourseInfo] = []
    sophomore: List[CourseInfo] = []
    junior: List[CourseInfo] = []
    senior: List[CourseInfo] = []
    graduate: List[CourseInfo] = []
    interdisciplinary: List[CourseInfo] = []

    class Config:
        from_attributes = True


class ArchiveRead(BaseModel):
    id: int
    name: str
    academic_year: int
    archive_type: ArchiveType
    professor: str
    has_answers: bool
    created_at: datetime
    uploader_id: Optional[int] = None
    download_count: int = 0

    class Config:
        from_attributes = True


class ArchiveDiscussionMessageRead(BaseModel):
    id: int
    archive_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    name: str
    category: CourseCategory
    order_index: Optional[int] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[CourseCategory] = None
    order_index: Optional[int] = None


class CourseReorder(BaseModel):
    category: CourseCategory
    course_ids: List[int]


class CourseRead(BaseModel):
    id: int
    name: str
    category: CourseCategory
    order_index: int = 0

    class Config:
        from_attributes = True


class ArchiveUpdateCourse(BaseModel):
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    course_category: Optional[CourseCategory] = None


class CourseSubmissionCreate(BaseModel):
    name: str
    category: CourseCategory


class SubmissionDecision(BaseModel):
    note: Optional[str] = None


class CourseSubmissionRead(BaseModel):
    id: int
    name: str
    category: CourseCategory
    status: SubmissionStatus
    requester_id: int
    reviewer_id: Optional[int] = None
    review_note: Optional[str] = None
    created_course_id: Optional[int] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArchiveSubmissionRead(BaseModel):
    id: int
    subject: str
    category: CourseCategory
    name: str
    academic_year: int
    archive_type: ArchiveType
    professor: str
    has_answers: bool
    status: SubmissionStatus
    requester_id: int
    reviewer_id: Optional[int] = None
    review_note: Optional[str] = None
    created_archive_id: Optional[int] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
