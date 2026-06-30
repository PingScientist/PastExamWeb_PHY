from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from minio.error import S3Error
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.models import (
    Archive,
    ArchiveDiscussionMessage,
    ArchiveSubmission,
    Course,
    CourseCategoryConfig,
    CourseSubmission,
    Notification,
    SubmissionStatus,
    TrashEntityType,
    TrashItem,
    User,
)
from app.utils.auth import get_current_user
from app.utils.storage import get_minio_client

router = APIRouter()


class TrashActionRequest(BaseModel):
    item_type: TrashEntityType
    item_id: int


def _to_trash_item(
    *,
    item_type: TrashEntityType,
    item_id: int,
    display_name: str,
    deleted_at,
    deleted_by_id: Optional[int],
    deleted_by_name: Optional[str] = None,
    status: Optional[str] = None,
    academic_year: Optional[int] = None,
    academic_term: Optional[str] = None,
    dependencies: Optional[list[str]] = None,
) -> TrashItem:
    return TrashItem(
        item_type=item_type,
        id=item_id,
        display_name=display_name,
        academic_year=academic_year,
        academic_term=academic_term,
        deleted_at=deleted_at,
        deleted_by_id=deleted_by_id,
        deleted_by_name=deleted_by_name,
        status=status,
        reason=None,
        dependencies=_build_dependencies(dependencies or []),
    )


def _build_dependencies(messages: list[str]) -> list[str]:
    return [item for item in messages if item]


def _format_academic_term(value: Optional[int]) -> Optional[str]:
    if not value:
        return None
    if 1000 <= value < 2000:
        year = value // 10
        semester = value % 10
        return f"{year}{'上' if semester == 1 else '下'}學期"
    return f"{value} 年"


def _format_deleted_by(users_by_id: dict[int, User], user_id: Optional[int]) -> Optional[str]:
    if not user_id:
        return None
    user = users_by_id.get(user_id)
    if not user:
        return f"已刪除使用者 #{user_id}"
    return user.nickname or user.name or user.email or f"使用者 #{user_id}"


async def _count_rows(db: SQLModelAsyncSession, statement) -> int:
    result = await db.execute(statement)
    return int(result.scalar() or 0)


async def _get_category_dependency_messages(db: SQLModelAsyncSession, category: CourseCategoryConfig) -> list[str]:
    active_courses = await _count_rows(
        db,
        select(func.count(Course.id)).where(
            Course.category == category.key,
            Course.deleted_at.is_(None),
        ),
    )
    trashed_courses = await _count_rows(
        db,
        select(func.count(Course.id)).where(
            Course.category == category.key,
            Course.deleted_at.is_not(None),
        ),
    )
    course_submissions = await _count_rows(
        db,
        select(func.count(CourseSubmission.id)).where(
            CourseSubmission.category == category.key,
        ),
    )
    active_archive_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            or_(
                ArchiveSubmission.category == category.key,
                ArchiveSubmission.requested_category_key == category.key,
            ),
            ArchiveSubmission.status != SubmissionStatus.DELETED,
            ArchiveSubmission.deleted_at.is_(None),
        ),
    )
    trashed_archive_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            or_(
                ArchiveSubmission.category == category.key,
                ArchiveSubmission.requested_category_key == category.key,
            ),
            or_(
                ArchiveSubmission.deleted_at.is_not(None),
                ArchiveSubmission.status == SubmissionStatus.DELETED,
            ),
        ),
    )

    return [
        f"active courses: {active_courses}" if active_courses else "",
        f"trashed courses: {trashed_courses}" if trashed_courses else "",
        f"course submissions: {course_submissions}" if course_submissions else "",
        f"archive submissions (active): {active_archive_submissions}" if active_archive_submissions else "",
        f"archive submissions (trashed): {trashed_archive_submissions}" if trashed_archive_submissions else "",
    ]


async def _get_course_dependency_messages(db: SQLModelAsyncSession, course: Course) -> list[str]:
    active_archives = await _count_rows(
        db,
        select(func.count(Archive.id)).where(
            Archive.course_id == course.id,
            Archive.deleted_at.is_(None),
        ),
    )
    trashed_archives = await _count_rows(
        db,
        select(func.count(Archive.id)).where(
            Archive.course_id == course.id,
            Archive.deleted_at.is_not(None),
        ),
    )

    return [
        f"active archives: {active_archives}" if active_archives else "",
        f"trashed archives: {trashed_archives}" if trashed_archives else "",
    ]


async def _get_archive_dependency_messages(db: SQLModelAsyncSession, archive: Archive) -> list[str]:
    linked_comments = await _count_rows(
        db,
        select(func.count(ArchiveDiscussionMessage.id)).where(
            ArchiveDiscussionMessage.archive_id == archive.id,
            ArchiveDiscussionMessage.deleted_at.is_(None),
        ),
    )
    active_linked_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            ArchiveSubmission.created_archive_id == archive.id,
            ArchiveSubmission.deleted_at.is_(None),
            ArchiveSubmission.status != SubmissionStatus.DELETED,
        ),
    )
    trashed_linked_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            ArchiveSubmission.created_archive_id == archive.id,
            or_(
                ArchiveSubmission.deleted_at.is_not(None),
                ArchiveSubmission.status == SubmissionStatus.DELETED,
            ),
        ),
    )

    return [
        f"active comments: {linked_comments}" if linked_comments else "",
        f"active linked submissions: {active_linked_submissions}" if active_linked_submissions else "",
        f"trashed linked submissions: {trashed_linked_submissions}" if trashed_linked_submissions else "",
    ]


async def _get_user_dependency_messages(db: SQLModelAsyncSession, user: User) -> list[str]:
    active_archives = await _count_rows(
        db,
        select(func.count(Archive.id)).where(
            Archive.uploader_id == user.id,
            Archive.deleted_at.is_(None),
        ),
    )
    trashed_archives = await _count_rows(
        db,
        select(func.count(Archive.id)).where(
            Archive.uploader_id == user.id,
            Archive.deleted_at.is_not(None),
        ),
    )
    active_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            or_(
                ArchiveSubmission.owner_id == user.id,
                ArchiveSubmission.requester_id == user.id,
            ),
            ArchiveSubmission.status != SubmissionStatus.DELETED,
            ArchiveSubmission.deleted_at.is_(None),
        ),
    )
    trashed_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            or_(
                ArchiveSubmission.owner_id == user.id,
                ArchiveSubmission.requester_id == user.id,
            ),
            or_(
                ArchiveSubmission.deleted_at.is_not(None),
                ArchiveSubmission.status == SubmissionStatus.DELETED,
            ),
        ),
    )

    return [
        f"active uploads: {active_archives}" if active_archives else "",
        f"trashed uploads: {trashed_archives}" if trashed_archives else "",
        f"active archive submissions: {active_submissions}" if active_submissions else "",
        f"trashed archive submissions: {trashed_submissions}" if trashed_submissions else "",
    ]


async def _get_submission_dependency_messages(db: SQLModelAsyncSession, submission: ArchiveSubmission) -> list[str]:
    if not submission.created_archive_id:
        return []

    linked_archive = await db.get(Archive, submission.created_archive_id)
    if not linked_archive:
        return ["linked archive: missing"]

    linked_comments = await _count_rows(
        db,
        select(func.count(ArchiveDiscussionMessage.id)).where(
            ArchiveDiscussionMessage.archive_id == linked_archive.id,
            ArchiveDiscussionMessage.deleted_at.is_(None),
        ),
    )
    trashed_comments = await _count_rows(
        db,
        select(func.count(ArchiveDiscussionMessage.id)).where(
            ArchiveDiscussionMessage.archive_id == linked_archive.id,
            ArchiveDiscussionMessage.deleted_at.is_not(None),
        ),
    )
    linked_other_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            ArchiveSubmission.created_archive_id == linked_archive.id,
            ArchiveSubmission.id != submission.id,
            ArchiveSubmission.deleted_at.is_(None),
            ArchiveSubmission.status != SubmissionStatus.DELETED,
        ),
    )
    trashed_submissions = await _count_rows(
        db,
        select(func.count(ArchiveSubmission.id)).where(
            ArchiveSubmission.created_archive_id == linked_archive.id,
            ArchiveSubmission.id != submission.id,
            or_(
                ArchiveSubmission.deleted_at.is_not(None),
                ArchiveSubmission.status == SubmissionStatus.DELETED,
            ),
        ),
    )
    archive_status = [f"linked archive: {1 if linked_archive else 0}"]
    if linked_archive and linked_archive.deleted_at is None:
        archive_status.append("linked archive: active")

    return [
        *archive_status,
        f"active comments: {linked_comments}" if linked_comments else "",
        f"trashed comments: {trashed_comments}" if trashed_comments else "",
        f"active linked archive submissions: {linked_other_submissions}" if linked_other_submissions else "",
        f"trashed linked archive submissions: {trashed_submissions}" if trashed_submissions else "",
    ]


def _build_trash_error(item_label: str, dependencies: list[str]) -> str:
    if not dependencies:
        return item_label
    if len(dependencies) == 1:
        return f"{item_label}: {dependencies[0]}"
    return f"{item_label}; blockers: {', '.join(dependencies)}"


def _is_submission_trashed(submission: ArchiveSubmission) -> bool:
    return submission.deleted_at is not None or submission.status == SubmissionStatus.DELETED


def _blocker(item_type: str, item_id: int | None, name: str, status_value: str = "active") -> dict:
    return {
        "type": item_type,
        "id": item_id,
        "name": name,
        "status": status_value,
    }


def _blocker_with_reason(
    item_type: str,
    item_id: int | None,
    name: str,
    status_value: str = "active",
    *,
    reason: Optional[str] = None,
) -> dict:
    blocker = _blocker(item_type, item_id, name, status_value)
    if reason:
        blocker["reason"] = reason
    return blocker


def _is_created_archive_id_nullable() -> bool:
    try:
        column = ArchiveSubmission.__table__.c.get("created_archive_id")
        if column is None:
            return True
        return bool(column.nullable)
    except Exception:
        return True


def _blocked(message: str, blockers: list[dict]) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "success": False,
            "deleted": 0,
            "failed": 1,
            "message": message,
            "blockingDependencies": blockers,
            "warnings": [],
        },
    )


def _delete_result(
    *,
    item_type: TrashEntityType,
    item_id: int,
    name: str,
    deleted: int,
    details: Optional[list[dict]] = None,
    warnings: Optional[list[str]] = None,
) -> dict:
    return {
        "success": True,
        "deleted": deleted,
        "deleted_count": deleted,
        "failed": 0,
        "failed_count": 0,
        "skipped": 0,
        "message": "永久刪除完成",
        "details": details
        or [
            {
                "type": item_type.value,
                "id": item_id,
                "name": name,
            }
        ],
        "warnings": warnings or [],
    }


async def _get_active_course_blockers(db: SQLModelAsyncSession, category: CourseCategoryConfig) -> list[dict]:
    courses = (
        await db.execute(
            select(Course).where(
                Course.category == category.key,
                Course.deleted_at.is_(None),
            )
        )
    ).scalars().all()
    return [_blocker("course", course.id, course.name) for course in courses]


async def _get_active_archive_blockers(db: SQLModelAsyncSession, course: Course) -> list[dict]:
    archives = (
        await db.execute(
            select(Archive).where(
                Archive.course_id == course.id,
                Archive.deleted_at.is_(None),
            )
        )
    ).scalars().all()
    return [_blocker("archive", archive.id, archive.name) for archive in archives]


async def _get_active_category_submission_blockers(
    db: SQLModelAsyncSession,
    category: CourseCategoryConfig,
) -> list[dict]:
    course_submissions = (
        await db.execute(
            select(CourseSubmission).where(
                CourseSubmission.category == category.key,
                CourseSubmission.status != SubmissionStatus.DELETED,
            )
        )
    ).scalars().all()
    archive_submissions = (
        await db.execute(
            select(ArchiveSubmission).where(
                or_(
                    ArchiveSubmission.category == category.key,
                    ArchiveSubmission.requested_category_key == category.key,
                ),
                ArchiveSubmission.status != SubmissionStatus.DELETED,
                ArchiveSubmission.deleted_at.is_(None),
            )
        )
    ).scalars().all()
    return [
        *[_blocker("course_submission", item.id, item.name, item.status.value) for item in course_submissions],
        *[
            _blocker("archive_submission", item.id, f"{item.subject} / {item.name}", item.status.value)
            for item in archive_submissions
        ],
    ]


async def _get_active_user_blockers(db: SQLModelAsyncSession, user: User) -> list[dict]:
    archives = (
        await db.execute(
            select(Archive).where(
                Archive.uploader_id == user.id,
                Archive.deleted_at.is_(None),
            )
        )
    ).scalars().all()
    submissions = (
        await db.execute(
            select(ArchiveSubmission).where(
                or_(
                    ArchiveSubmission.owner_id == user.id,
                    ArchiveSubmission.requester_id == user.id,
                ),
                ArchiveSubmission.status != SubmissionStatus.DELETED,
                ArchiveSubmission.deleted_at.is_(None),
            )
        )
    ).scalars().all()
    return [
        *[_blocker("archive", item.id, item.name) for item in archives],
        *[
            _blocker("archive_submission", item.id, f"{item.subject} / {item.name}", item.status.value)
            for item in submissions
        ],
    ]


async def _remove_storage_object_if_unreferenced(
    db: SQLModelAsyncSession,
    object_name: Optional[str],
    warnings: list[str],
    *,
    exclude_archive_id: Optional[int] = None,
    exclude_submission_ids: Optional[list[int]] = None,
) -> int:
    if not object_name:
        return 0

    archive_query = select(func.count(Archive.id)).where(
        Archive.object_name == object_name,
        Archive.deleted_at.is_(None),
    )
    if exclude_archive_id is not None:
        archive_query = archive_query.where(Archive.id != exclude_archive_id)

    submission_query = select(func.count(ArchiveSubmission.id)).where(
        ArchiveSubmission.object_name == object_name,
        ArchiveSubmission.deleted_at.is_(None),
        ArchiveSubmission.status != SubmissionStatus.DELETED,
    )
    if exclude_submission_ids:
        submission_query = submission_query.where(~ArchiveSubmission.id.in_(exclude_submission_ids))

    active_refs = await _count_rows(db, archive_query) + await _count_rows(db, submission_query)
    if active_refs:
        warnings.append(f"Storage object kept because active records still reference it: {object_name}")
        return 0

    try:
        get_minio_client().remove_object(settings.MINIO_BUCKET_NAME, object_name)
        return 1
    except S3Error as exc:
        if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            warnings.append(f"Storage object was already missing: {object_name}")
            return 0
        warnings.append(f"Storage object delete warning for {object_name}: {exc}")
        return 0
    except Exception as exc:
        warnings.append(f"Storage object delete warning for {object_name}: {exc}")
        return 0


async def _hard_delete_archive(
    db: SQLModelAsyncSession,
    archive: Archive,
    warnings: list[str],
) -> dict:
    if archive.deleted_at is None:
        raise _blocked(
            "仍有未刪除的考古題依附於此項目",
            [_blocker("archive", archive.id, archive.name)],
        )

    messages = (
        await db.execute(
            select(ArchiveDiscussionMessage).where(ArchiveDiscussionMessage.archive_id == archive.id)
        )
    ).scalars().all()
    submissions = (
        await db.execute(
            select(ArchiveSubmission).where(ArchiveSubmission.created_archive_id == archive.id)
        )
    ).scalars().all()

    deleted_submission_ids = [
        item.id for item in submissions if item is not None and _is_submission_trashed(item) and item.id is not None
    ]
    active_submission_ids = [
        item.id for item in submissions if item is not None and not _is_submission_trashed(item)
    ]
    if active_submission_ids:
        if not _is_created_archive_id_nullable():
            blockers = [
                _blocker_with_reason(
                    "archive_submission",
                    submission.id,
                    f"{submission.subject} / {submission.name}",
                    submission.status.value,
                    reason="活躍投稿仍參照此考古題，且 created_archive_id 欄位不可為空",
                )
                for submission in submissions
                if submission and not _is_submission_trashed(submission)
            ]
            raise _blocked(
                "仍有活躍投稿仍參照此考古題，請先行處理後再刪除",
                blockers,
            )
        for submission in submissions:
            if not _is_submission_trashed(submission):
                submission.created_archive_id = None
                warnings.append(
                    f"已移除投稿 {submission.id} 的 created_archive_id 關聯: archive #{archive.id}"
                )

    deleted_submissions = 0
    unlinked_submissions = len(active_submission_ids)
    for submission in submissions:
        if _is_submission_trashed(submission):
            await db.delete(submission)
            deleted_submissions += 1

    deleted_objects = await _remove_storage_object_if_unreferenced(
        db,
        archive.object_name,
        warnings,
        exclude_archive_id=archive.id,
        exclude_submission_ids=deleted_submission_ids,
    )

    for message in messages:
        await db.delete(message)
    await db.delete(archive)

    deleted_count = 1 + len(messages) + deleted_submissions
    return {
        "type": "archive",
        "id": archive.id,
        "name": archive.name,
        "deletedChildren": {
            "comments": len(messages),
            "linkedSubmissionsDeleted": deleted_submissions,
            "linkedSubmissionsUnlinked": unlinked_submissions,
            "files": deleted_objects,
        },
        "deleted": deleted_count,
    }


async def _hard_delete_submission(
    db: SQLModelAsyncSession,
    submission: ArchiveSubmission,
    warnings: list[str],
) -> dict:
    if not _is_submission_trashed(submission):
        raise _blocked(
            "仍有未刪除的投稿資料依附於此項目",
            [_blocker("archive_submission", submission.id, f"{submission.subject} / {submission.name}", submission.status.value)],
        )

    if submission.created_archive_id:
        archive = await db.get(Archive, submission.created_archive_id)
        if archive and archive.deleted_at is not None:
            return await _hard_delete_archive(db, archive, warnings)

    deleted_objects = await _remove_storage_object_if_unreferenced(
        db,
        submission.object_name,
        warnings,
        exclude_submission_ids=[submission.id] if submission.id is not None else [],
    )
    await db.delete(submission)
    return {
        "type": "archive_submission",
        "id": submission.id,
        "name": f"{submission.subject} / {submission.name}",
        "deletedChildren": {
            "files": deleted_objects,
        },
        "deleted": 1,
    }


async def _hard_delete_course(
    db: SQLModelAsyncSession,
    course: Course,
    warnings: list[str],
) -> dict:
    blockers = await _get_active_archive_blockers(db, course)
    if blockers:
        raise _blocked("仍有未刪除的考古題依附於此課程", blockers)

    trashed_archives = (
        await db.execute(
            select(Archive).where(
                Archive.course_id == course.id,
                Archive.deleted_at.is_not(None),
            )
        )
    ).scalars().all()

    details = []
    deleted_count = 1
    for archive in trashed_archives:
        detail = await _hard_delete_archive(db, archive, warnings)
        details.append(detail)
        deleted_count += detail.get("deleted", 0)

    await db.delete(course)
    return {
        "type": "course",
        "id": course.id,
        "name": course.name,
        "deletedChildren": {
            "archives": len(trashed_archives),
        },
        "children": details,
        "deleted": deleted_count,
    }


async def _hard_delete_category(
    db: SQLModelAsyncSession,
    category: CourseCategoryConfig,
    warnings: list[str],
) -> dict:
    blockers = [
        *(await _get_active_course_blockers(db, category)),
        *(await _get_active_category_submission_blockers(db, category)),
    ]
    if blockers:
        raise _blocked("仍有未刪除的課程或投稿依附於此分類", blockers)

    trashed_courses = (
        await db.execute(
            select(Course).where(
                Course.category == category.key,
                Course.deleted_at.is_not(None),
            )
        )
    ).scalars().all()
    trashed_submissions = (
        await db.execute(
            select(ArchiveSubmission).where(
                or_(
                    ArchiveSubmission.category == category.key,
                    ArchiveSubmission.requested_category_key == category.key,
                ),
                or_(
                    ArchiveSubmission.deleted_at.is_not(None),
                    ArchiveSubmission.status == SubmissionStatus.DELETED,
                ),
            )
        )
    ).scalars().all()

    details = []
    deleted_count = 1
    for submission in trashed_submissions:
        if submission.id is None:
            continue
        current_submission = await db.get(ArchiveSubmission, submission.id)
        if not current_submission:
            continue
        detail = await _hard_delete_submission(db, current_submission, warnings)
        details.append(detail)
        deleted_count += detail.get("deleted", 0)

    for course in trashed_courses:
        current_course = await db.get(Course, course.id)
        if not current_course:
            continue
        detail = await _hard_delete_course(db, current_course, warnings)
        details.append(detail)
        deleted_count += detail.get("deleted", 0)

    await db.delete(category)
    return {
        "type": "course_category",
        "id": category.id,
        "name": category.name,
        "deletedChildren": {
            "courses": len(trashed_courses),
            "submissions": len(trashed_submissions),
        },
        "children": details,
        "deleted": deleted_count,
    }


async def _hard_delete_user(
    db: SQLModelAsyncSession,
    user: User,
    warnings: list[str],
) -> dict:
    blockers = await _get_active_user_blockers(db, user)
    if blockers:
        raise _blocked("仍有未刪除的上傳或投稿依附於此使用者", blockers)

    trashed_archives = (
        await db.execute(
            select(Archive).where(
                Archive.uploader_id == user.id,
                Archive.deleted_at.is_not(None),
            )
        )
    ).scalars().all()
    trashed_submissions = (
        await db.execute(
            select(ArchiveSubmission).where(
                or_(
                    ArchiveSubmission.owner_id == user.id,
                    ArchiveSubmission.requester_id == user.id,
                ),
                or_(
                    ArchiveSubmission.deleted_at.is_not(None),
                    ArchiveSubmission.status == SubmissionStatus.DELETED,
                ),
            )
        )
    ).scalars().all()

    details = []
    deleted_count = 1
    for submission in trashed_submissions:
        current_submission = await db.get(ArchiveSubmission, submission.id)
        if not current_submission:
            continue
        detail = await _hard_delete_submission(db, current_submission, warnings)
        details.append(detail)
        deleted_count += detail.get("deleted", 0)

    for archive in trashed_archives:
        current_archive = await db.get(Archive, archive.id)
        if not current_archive:
            continue
        detail = await _hard_delete_archive(db, current_archive, warnings)
        details.append(detail)
        deleted_count += detail.get("deleted", 0)

    await db.delete(user)
    return {
        "type": "user",
        "id": user.id,
        "name": user.name,
        "deletedChildren": {
            "archives": len(trashed_archives),
            "submissions": len(trashed_submissions),
        },
        "children": details,
        "deleted": deleted_count,
    }


@router.get("", response_model=List[TrashItem])
async def list_trash_items(
    item_type: Optional[TrashEntityType] = Query(default=None),
    current_user=Depends(get_current_user),
    db: SQLModelAsyncSession = Depends(get_session),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    users_by_id = {
        user.id: user
        for user in (await db.execute(select(User))).scalars().all()
        if user.id is not None
    }
    items: list[TrashItem] = []

    if item_type in (None, TrashEntityType.COURSE_CATEGORY):
        categories = (
            await db.execute(
                select(CourseCategoryConfig)
                .where(CourseCategoryConfig.deleted_at.is_not(None))
                .order_by(CourseCategoryConfig.deleted_at.desc())
            )
        ).scalars().all()
        for category in categories:
            items.append(
                _to_trash_item(
                    item_type=TrashEntityType.COURSE_CATEGORY,
                    item_id=category.id,
                    display_name=f"{category.name} ({category.key})",
                    deleted_at=category.deleted_at,
                    deleted_by_id=category.deleted_by_id,
                    deleted_by_name=_format_deleted_by(users_by_id, category.deleted_by_id),
                    status="deleted",
                    dependencies=await _get_category_dependency_messages(db, category),
                )
            )

    if item_type in (None, TrashEntityType.COURSE):
        courses = (
            await db.execute(
                select(Course)
                .where(Course.deleted_at.is_not(None))
                .order_by(Course.deleted_at.desc())
            )
        ).scalars().all()
        for course in courses:
            items.append(
                _to_trash_item(
                    item_type=TrashEntityType.COURSE,
                    item_id=course.id,
                    display_name=f"{course.name} ({course.category})",
                    deleted_at=course.deleted_at,
                    deleted_by_id=course.deleted_by_id,
                    deleted_by_name=_format_deleted_by(users_by_id, course.deleted_by_id),
                    status="deleted",
                    dependencies=await _get_course_dependency_messages(db, course),
                )
            )

    if item_type in (None, TrashEntityType.ARCHIVE):
        archives = (
            await db.execute(
                select(Archive)
                .where(Archive.deleted_at.is_not(None))
                .order_by(Archive.deleted_at.desc())
            )
        ).scalars().all()
        for archive in archives:
            items.append(
                _to_trash_item(
                    item_type=TrashEntityType.ARCHIVE,
                    item_id=archive.id,
                    display_name=archive.name,
                    academic_year=archive.academic_year,
                    academic_term=_format_academic_term(archive.academic_year),
                    deleted_at=archive.deleted_at,
                    deleted_by_id=archive.deleted_by_id,
                    deleted_by_name=_format_deleted_by(users_by_id, archive.deleted_by_id),
                    status="deleted",
                    dependencies=await _get_archive_dependency_messages(db, archive),
                )
            )

    if item_type in (None, TrashEntityType.NOTIFICATION):
        notifications = (
            await db.execute(
                select(Notification)
                .where(Notification.deleted_at.is_not(None))
                .order_by(Notification.deleted_at.desc())
            )
        ).scalars().all()
        for notification in notifications:
            items.append(
                _to_trash_item(
                    item_type=TrashEntityType.NOTIFICATION,
                    item_id=notification.id,
                    display_name=notification.title,
                    deleted_at=notification.deleted_at,
                    deleted_by_id=None,
                    deleted_by_name=None,
                    status="deleted",
                    dependencies=[],
                )
            )

    if item_type in (None, TrashEntityType.USER):
        users = (
            await db.execute(
                select(User).where(User.deleted_at.is_not(None)).order_by(User.deleted_at.desc())
            )
        ).scalars().all()
        for user in users:
            items.append(
                _to_trash_item(
                    item_type=TrashEntityType.USER,
                    item_id=user.id,
                    display_name=f"{user.name} ({user.email})",
                    deleted_at=user.deleted_at,
                    deleted_by_id=None,
                    deleted_by_name=None,
                    status="deleted",
                    dependencies=await _get_user_dependency_messages(db, user),
                )
            )

    if item_type in (None, TrashEntityType.ARCHIVE_SUBMISSION):
        submissions = (
            await db.execute(
                select(ArchiveSubmission)
                .where(
                    or_(
                        ArchiveSubmission.deleted_at.is_not(None),
                        ArchiveSubmission.status == SubmissionStatus.DELETED,
                    )
                )
                .order_by(ArchiveSubmission.deleted_at.desc(), ArchiveSubmission.reviewed_at.desc(), ArchiveSubmission.created_at.desc())
            )
        ).scalars().all()
        for submission in submissions:
            deleted_at = submission.deleted_at or submission.reviewed_at or submission.created_at
            items.append(
                _to_trash_item(
                    item_type=TrashEntityType.ARCHIVE_SUBMISSION,
                    item_id=submission.id,
                    display_name=f"{submission.subject} / {submission.name}",
                    academic_year=submission.academic_year,
                    academic_term=_format_academic_term(submission.academic_year),
                    deleted_at=deleted_at,
                    deleted_by_id=submission.deleted_by_id,
                    deleted_by_name=_format_deleted_by(users_by_id, submission.deleted_by_id),
                    status=submission.status.value,
                    dependencies=await _get_submission_dependency_messages(db, submission),
                )
            )

    return sorted(items, key=lambda item: item.deleted_at, reverse=True)


@router.post("/restore")
async def restore_trash_item(
    payload: TrashActionRequest,
    current_user=Depends(get_current_user),
    db: SQLModelAsyncSession = Depends(get_session),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    now = datetime.now(timezone.utc)

    if payload.item_type == TrashEntityType.COURSE_CATEGORY:
        category = await db.get(CourseCategoryConfig, payload.item_id)
        if not category or category.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        category.deleted_at = None
        category.restored_at = now
        category.restored_by_id = current_user.user_id
        category.deleted_by_id = None
        category.is_active = True
        await db.commit()
        return {"message": "Category restored"}

    if payload.item_type == TrashEntityType.COURSE:
        course = await db.get(Course, payload.item_id)
        if not course or course.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        category = (
            await db.execute(
                select(CourseCategoryConfig).where(CourseCategoryConfig.key == course.category)
            )
        ).scalar_one_or_none()
        if not category or category.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category is deleted; restore category before restoring this course.",
            )

        course.deleted_at = None
        course.deleted_by_id = None
        course.restored_at = now
        course.restored_by_id = current_user.user_id

        archives = (
            await db.execute(
                select(Archive).where(
                    Archive.course_id == course.id,
                    Archive.deleted_at.is_not(None),
                )
            )
        ).scalars().all()
        for archive in archives:
            archive.deleted_at = None
            archive.deleted_by_id = None
            archive.deleted_reason = None
            archive.restored_at = now
            archive.restored_by_id = current_user.user_id

        await db.commit()
        return {"message": "Course restored"}

    if payload.item_type == TrashEntityType.NOTIFICATION:
        notification = await db.get(Notification, payload.item_id)
        if not notification or notification.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        notification.deleted_at = None
        await db.commit()
        return {"message": "Notification restored"}

    if payload.item_type == TrashEntityType.ARCHIVE:
        archive = await db.get(Archive, payload.item_id)
        if not archive or archive.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found")

        course = await db.get(Course, archive.course_id)
        if not course or course.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course is deleted; restore course before restoring this archive.",
            )

        archive.deleted_at = None
        archive.deleted_by_id = None
        archive.deleted_reason = None
        archive.restored_at = now
        archive.restored_by_id = current_user.user_id
        await db.commit()
        return {"message": "Archive restored"}

    if payload.item_type == TrashEntityType.USER:
        user = await db.get(User, payload.item_id)
        if not user or user.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.deleted_at = None
        await db.commit()
        return {"message": "User restored"}

    if payload.item_type == TrashEntityType.ARCHIVE_SUBMISSION:
        submission = await db.get(ArchiveSubmission, payload.item_id)
        if not submission or submission.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

        linked_archive = None
        if submission.created_archive_id:
            linked_archive = await db.get(Archive, submission.created_archive_id)
            if linked_archive and linked_archive.deleted_at is not None:
                course = await db.get(Course, linked_archive.course_id)
                if course and course.deleted_at is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Cannot restore: linked course is deleted. Restore course first.",
                    )

                linked_archive.deleted_at = None
                linked_archive.deleted_by_id = None
                linked_archive.deleted_reason = None
                linked_archive.restored_at = now
                # ownership transfer to reviewer/admin
                linked_archive.uploader_id = current_user.user_id
                linked_archive.restored_by_id = current_user.user_id

        submission.deleted_at = None
        submission.delete_reason = None
        submission.deleted_by_id = None
        submission.owner_id = current_user.user_id
        submission.reviewed_at = now if submission.created_archive_id else None
        submission.reviewer_id = current_user.user_id
        submission.restored_at = now
        submission.restored_by_id = current_user.user_id

        if submission.created_archive_id:
            submission.status = SubmissionStatus.APPROVED
        else:
            submission.status = SubmissionStatus.PENDING

        await db.commit()
        return {"message": "Submission restored"}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported trash item type")


@router.delete("/bulk")
async def bulk_permanently_delete_trash_items(
    item_type: Optional[TrashEntityType] = Query(default=None),
    current_user=Depends(get_current_user),
    db: SQLModelAsyncSession = Depends(get_session),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    items = await list_trash_items(item_type=item_type, current_user=current_user, db=db)
    delete_order = {
        TrashEntityType.ARCHIVE_SUBMISSION: 0,
        TrashEntityType.ARCHIVE: 1,
        TrashEntityType.COURSE: 2,
        TrashEntityType.COURSE_CATEGORY: 3,
        TrashEntityType.NOTIFICATION: 4,
        TrashEntityType.USER: 5,
    }
    sorted_items = sorted(
        items,
        key=lambda item: delete_order.get(TrashEntityType(item.item_type), 99),
    )
    details: list[dict] = []
    failures: list[dict] = []
    skipped: list[dict] = []
    warnings: list[str] = []
    deleted_count = 0

    for item in sorted_items:
        trash_type = TrashEntityType(item.item_type)
        try:
            result = await _permanently_delete_trash_item(
                item_type=trash_type,
                item_id=item.id,
                db=db,
                warnings=warnings,
            )
            await db.commit()
            details.extend(result.get("details", []))
            deleted_count += int(result.get("deleted", result.get("deleted_count", 0)) or 0)
        except HTTPException as error:
            await db.rollback()
            if error.status_code == status.HTTP_404_NOT_FOUND:
                skipped.append({"item_type": trash_type.value, "id": item.id, "display_name": item.display_name})
                continue
            detail = error.detail if isinstance(error.detail, dict) else {"message": error.detail}
            failures.append(
                {
                    "type": trash_type.value,
                    "id": item.id,
                    "name": item.display_name,
                    "reason": detail.get("message", error.detail),
                    "blockingDependencies": detail.get("blockingDependencies", []),
                }
            )
        except Exception as error:
            await db.rollback()
            failures.append(
                {
                    "type": trash_type.value,
                    "id": item.id,
                    "name": item.display_name,
                    "reason": "永久刪除失敗，請稍後再試或查看伺服器日誌。",
                    "blockingDependencies": [],
                }
            )

    return {
        "success": True,
        "scope": item_type.value if item_type else "all",
        "deleted": deleted_count,
        "deleted_count": deleted_count,
        "failed": len(failures),
        "failed_count": len(failures),
        "skipped": len(skipped),
        "message": (
            "部分項目因仍有未刪除的依賴資料而無法永久刪除"
            if failures
            else "永久刪除完成"
        ),
        "details": details,
        "failures": failures,
        "skipped_items": skipped,
        "warnings": warnings,
    }


async def _permanently_delete_trash_item(
    *,
    item_type: TrashEntityType,
    item_id: int,
    db: SQLModelAsyncSession,
    warnings: list[str],
):
    if item_type == TrashEntityType.COURSE_CATEGORY:
        category = await db.get(CourseCategoryConfig, item_id)
        if not category or category.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        detail = await _hard_delete_category(db, category, warnings)
        return _delete_result(
            item_type=item_type,
            item_id=item_id,
            name=category.name,
            deleted=detail.get("deleted", 1),
            details=[detail],
            warnings=warnings,
        )

    if item_type == TrashEntityType.COURSE:
        course = await db.get(Course, item_id)
        if not course or course.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        detail = await _hard_delete_course(db, course, warnings)
        return _delete_result(
            item_type=item_type,
            item_id=item_id,
            name=course.name,
            deleted=detail.get("deleted", 1),
            details=[detail],
            warnings=warnings,
        )

    if item_type == TrashEntityType.USER:
        user = await db.get(User, item_id)
        if not user or user.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        detail = await _hard_delete_user(db, user, warnings)
        return _delete_result(
            item_type=item_type,
            item_id=item_id,
            name=user.name,
            deleted=detail.get("deleted", 1),
            details=[detail],
            warnings=warnings,
        )

    if item_type == TrashEntityType.ARCHIVE:
        archive = await db.get(Archive, item_id)
        if not archive or archive.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found")

        detail = await _hard_delete_archive(db, archive, warnings)
        return _delete_result(
            item_type=item_type,
            item_id=item_id,
            name=archive.name,
            deleted=detail.get("deleted", 1),
            details=[detail],
            warnings=warnings,
        )

    if item_type == TrashEntityType.NOTIFICATION:
        notification = await db.get(Notification, item_id)
        if not notification or notification.deleted_at is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        await db.delete(notification)
        return _delete_result(
            item_type=item_type,
            item_id=item_id,
            name=notification.title,
            deleted=1,
            warnings=warnings,
        )

    if item_type == TrashEntityType.ARCHIVE_SUBMISSION:
        submission = await db.get(ArchiveSubmission, item_id)
        if not submission or (
            submission.deleted_at is None and submission.status != SubmissionStatus.DELETED
        ):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

        detail = await _hard_delete_submission(db, submission, warnings)
        return _delete_result(
            item_type=item_type,
            item_id=item_id,
            name=f"{submission.subject} / {submission.name}",
            deleted=detail.get("deleted", 1),
            details=[detail],
            warnings=warnings,
        )

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported trash item type")


@router.delete("/{item_type}/{item_id}")
async def permanently_delete_trash_item(
    item_type: TrashEntityType,
    item_id: int,
    current_user=Depends(get_current_user),
    db: SQLModelAsyncSession = Depends(get_session),
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    warnings: list[str] = []
    try:
        result = await _permanently_delete_trash_item(
            item_type=item_type,
            item_id=item_id,
            db=db,
            warnings=warnings,
        )
        await db.commit()
        return result
    except HTTPException:
        await db.rollback()
        raise
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "deleted": 0,
                "failed": 1,
                "message": "永久刪除失敗，請稍後再試或查看伺服器日誌。",
                "blockingDependencies": [],
                "warnings": warnings,
            },
        )
