from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Any, List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


class CourseCategory(str, PyEnum):
    FRESHMAN = "fundamental"
    SOPHOMORE = "required"
    JUNIOR = "experience"
    SENIOR = "optional"
    GRADUATE = "graduate"
    INTERDISCIPLINARY = "math-department"
    GENERAL = "general"


class ArchiveType(str, PyEnum):
    QUIZ = "quiz"
    MIDTERM = "midterm"
    FINAL = "final"
    OTHER = "other"


class NotificationSeverity(str, PyEnum):
    INFO = "info"
    DANGER = "danger"


class TrashEntityType(str, PyEnum):
    ARCHIVE = "archive"
    ARCHIVE_SUBMISSION = "archive_submission"
    COURSE_CATEGORY = "course_category"
    COURSE = "course"
    NOTIFICATION = "notification"
    USER = "user"


class SubmissionStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELETED = "deleted"
    TAKEDOWN = "takedown"


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    oauth_provider: Optional[str] = Field(default=None)
    oauth_sub: Optional[str] = Field(default=None)
    email: str = Field(unique=True, index=True)
    name: str = Field(unique=True, index=True)
    nickname: Optional[str] = Field(default=None, index=True)
    show_level_title: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    password_hash: Optional[str] = Field(default=None)
    is_local: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    last_login: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    last_seen_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    last_logout: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    archives: List["Archive"] = Relationship(back_populates="uploader")


class UserPresenceSession(SQLModel, table=True):
    __tablename__ = "user_presence_sessions"
    __table_args__ = (
        Index("ix_user_presence_sessions_user_started", "user_id", "started_at"),
        Index("ix_user_presence_sessions_identifier", "session_identifier"),
        Index("ix_user_presence_sessions_last_seen", "last_seen_at"),
        Index("ix_user_presence_sessions_ended", "ended_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    session_identifier: str = Field(sa_column=Column(String(64), nullable=False))
    started_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    last_seen_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    ended_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class CourseCategoryConfig(SQLModel, table=True):
    __tablename__ = "course_category_configs"
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    label: str = Field(default="")
    icon: str = Field(default="pi pi-fw pi-book")
    badge_color: str = Field(
        default="blue",
        sa_column=Column(String, nullable=False, server_default="blue"),
    )
    order_index: int = Field(default=0, index=True)
    is_active: bool = Field(default=True, index=True)
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
    deleted_by_id: Optional[int] = Field(default=None)
    restored_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    restored_by_id: Optional[int] = Field(default=None)


class SystemSetting(SQLModel, table=True):
    __tablename__ = "system_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(
        sa_column=Column(String(128), nullable=False, unique=True, index=True)
    )
    value: Any = Field(sa_column=Column(JSONB, nullable=False))
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
    updated_by_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


class Course(SQLModel, table=True):
    __tablename__ = "courses"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    category: str = Field(index=True)
    order_index: int = Field(default=0, index=True)
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    deleted_by_id: Optional[int] = Field(default=None)
    restored_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    restored_by_id: Optional[int] = Field(default=None)

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
    deleted_by_id: Optional[int] = Field(default=None)
    deleted_reason: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    restored_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    restored_by_id: Optional[int] = Field(default=None)


class CourseSubmission(SQLModel, table=True):
    __tablename__ = "course_submissions"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    category: str = Field(index=True)
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
    category: str = Field(index=True)
    name: str
    academic_year: int
    archive_type: ArchiveType
    professor: str = Field(index=True)
    has_answers: bool = False
    object_name: str
    requested_course_name: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    requested_category_key: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    requested_category_name: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    requested_category_label: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    requested_category_icon: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    status: SubmissionStatus = Field(default=SubmissionStatus.PENDING, index=True)
    requester_id: int = Field(foreign_key="users.id", index=True)
    owner_id: Optional[int] = Field(default=None)
    reviewer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    review_note: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    is_admin_upload: bool = Field(default=False)
    lifecycle_reason: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    created_archive_id: Optional[int] = Field(default=None, foreign_key="archives.id")
    deleted_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    deleted_by_id: Optional[int] = Field(default=None)
    delete_reason: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    restored_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    restored_by_id: Optional[int] = Field(default=None)
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
    is_pinned: bool = Field(default=False, index=True)
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
    show_level_title: bool = True
    is_admin: bool
    is_local: bool
    last_login: Optional[datetime]
    last_login_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    last_logout_at: Optional[datetime] = None
    is_online: bool = False
    online_status_label: Optional[str] = None
    contributor_experience: int = 0

    class Config:
        from_attributes = True


class OnlineStatisticsPoint(BaseModel):
    start: datetime
    end: datetime
    at: datetime
    count: int
    has_data: bool


class OnlineStatisticsRead(BaseModel):
    range: str
    bucket_minutes: int
    timezone: str = "UTC"
    online_timeout_seconds: int
    current_online: int
    peak_online: int
    average_online: float
    history_started_at: Optional[datetime] = None
    points: List[OnlineStatisticsPoint] = Field(default_factory=list)


class SubmissionStatisticsSummary(BaseModel):
    total: int
    peak: int
    average: float


class SubmissionStatisticsPoint(BaseModel):
    start: datetime
    end: datetime
    count: int


class SubmissionStatisticsRead(BaseModel):
    mode: str
    range: str
    timezone: str
    bucket_minutes: int
    range_start: datetime
    range_end: datetime
    summary: SubmissionStatisticsSummary
    points: List[SubmissionStatisticsPoint] = Field(default_factory=list)


class UserOnlineDurationPoint(BaseModel):
    start: datetime
    end: datetime
    duration_seconds: int
    has_data: bool = False


class UserOnlineDurationRead(BaseModel):
    user_id: int
    mode: str
    timezone: str
    online_timeout_seconds: int
    range_start: datetime
    range_end: datetime
    history_started_at: Optional[datetime] = None
    points: List[UserOnlineDurationPoint] = Field(default_factory=list)


class UserSubmissionStatusCounts(BaseModel):
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    takedown: int = 0
    deleted: int = 0


class UserSubmissionRecordRead(BaseModel):
    id: int
    status: SubmissionStatus
    archive_type: ArchiveType
    course_name: str
    exam_name: str
    academic_year: int
    professor: str
    has_answers: bool = False
    requested_course_name: Optional[str] = None
    requested_category_key: Optional[str] = None
    is_admin_upload: bool = False
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None


class UserSubmissionStatsRead(BaseModel):
    user_id: int
    name: str
    contributor_experience: int = 0
    total_count: int = 0
    status_counts: UserSubmissionStatusCounts
    records_total: int = 0
    submission_records: List[UserSubmissionRecordRead] = Field(default_factory=list)


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    is_admin: bool = False


class UserPasswordResetRequest(BaseModel):
    new_password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


class UserNicknameUpdate(BaseModel):
    nickname: str
    show_level_title: Optional[bool] = None


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
    courses: dict[str, List[CourseInfo]] = {}

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
    source_submission_ids: List[int] = []

    class Config:
        from_attributes = True


class ArchiveDiscussionMessageRead(BaseModel):
    id: int
    archive_id: int
    user_id: int
    user_name: str
    author_show_level_title: bool = False
    author_experience: Optional[int] = None
    content: str
    is_pinned: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    name: str
    category: str
    order_index: Optional[int] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    order_index: Optional[int] = None


class CourseReorder(BaseModel):
    category: str
    course_ids: List[int]


class CourseRead(BaseModel):
    id: int
    name: str
    category: str
    order_index: int = 0

    class Config:
        from_attributes = True


class ArchiveUpdateCourse(BaseModel):
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    course_category: Optional[str] = None


class CourseSubmissionCreate(BaseModel):
    name: str
    category: str


class CourseCategoryCreate(BaseModel):
    key: str
    name: str
    label: str = ""
    icon: str = "pi pi-fw pi-book"
    badge_color: Optional[str] = None
    order_index: Optional[int] = None


class CourseCategoryUpdate(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    label: Optional[str] = None
    icon: Optional[str] = None
    badge_color: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class CourseCategoryReorder(BaseModel):
    category_ids: List[int]


class CourseCategoryRead(BaseModel):
    id: int
    key: str
    name: str
    label: str
    icon: str
    badge_color: str = "blue"
    order_index: int
    is_active: bool

    class Config:
        from_attributes = True


class SubmissionDecision(BaseModel):
    note: Optional[str] = None


class CourseSubmissionRead(BaseModel):
    id: int
    name: str
    category: str
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
    category: str
    name: str
    academic_year: int
    archive_type: ArchiveType
    professor: str
    has_answers: bool
    requested_course_name: Optional[str] = None
    requested_category_key: Optional[str] = None
    requested_category_name: Optional[str] = None
    requested_category_label: Optional[str] = None
    requested_category_icon: Optional[str] = None
    status: SubmissionStatus
    requester_id: int
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    is_admin_upload: bool = False
    reviewer_id: Optional[int] = None
    reviewer_name: Optional[str] = None
    reviewer_email: Optional[str] = None
    review_note: Optional[str] = None
    created_archive_id: Optional[int] = None
    lifecycle_reason: Optional[str] = None
    linked_archive_deleted: bool = False
    linked_course_deleted: bool = False
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArchiveSubmissionComparisonRead(ArchiveSubmissionRead):
    can_takedown: bool = False


class CourseSubmissionUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


class ArchiveSubmissionUpdate(BaseModel):
    subject: Optional[str] = None
    category: Optional[str] = None
    name: Optional[str] = None
    academic_year: Optional[int] = None
    archive_type: Optional[ArchiveType] = None
    professor: Optional[str] = None
    has_answers: Optional[bool] = None
    requested_course_name: Optional[str] = None
    requested_category_key: Optional[str] = None
    requested_category_name: Optional[str] = None
    requested_category_label: Optional[str] = None
    requested_category_icon: Optional[str] = None


class TrashItem(BaseModel):
    item_type: TrashEntityType
    id: int
    display_name: str
    academic_year: Optional[int] = None
    academic_term: Optional[str] = None
    deleted_at: datetime
    deleted_by_id: Optional[int] = None
    deleted_by_name: Optional[str] = None
    status: Optional[str] = None
    parent_type: Optional[str] = None
    parent_id: Optional[int] = None
    parent_name: Optional[str] = None
    created_archive_id: Optional[int] = None
    source_submission_id: Optional[int] = None
    course_id: Optional[int] = None
    course_name: Optional[str] = None
    reason: Optional[str] = None
    canRestore: Optional[bool] = None
    canPermanentDelete: Optional[bool] = None
    dependencies: List[str] = []
