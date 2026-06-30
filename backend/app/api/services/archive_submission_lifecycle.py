from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from minio.error import S3Error
from sqlalchemy import func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from app.core.config import settings
from app.models.models import Archive, ArchiveDiscussionMessage, ArchiveSubmission, SubmissionStatus
from app.utils.storage import get_minio_client

LIFECYCLE_ARCHIVE_TRASHED = "archive_trashed"
LIFECYCLE_COURSE_TRASHED = "course_trashed"
LIFECYCLE_LINKED_ARCHIVE_PERMANENTLY_DELETED = "linked_archive_permanently_deleted"


@dataclass
class ArchiveSubmissionGroup:
    archives: list[Archive] = field(default_factory=list)
    submissions: list[ArchiveSubmission] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def is_archive_submission_trashed(submission: ArchiveSubmission) -> bool:
    return submission.deleted_at is not None or submission.status == SubmissionStatus.DELETED


async def collect_archive_submission_group(
    db: SQLModelAsyncSession,
    *,
    archive: Optional[Archive] = None,
    submission: Optional[ArchiveSubmission] = None,
) -> ArchiveSubmissionGroup:
    group = ArchiveSubmissionGroup()
    archive_ids: set[int] = set()
    submission_ids: set[int] = set()

    def add_archive(item: Optional[Archive]) -> None:
        if item and item.id is not None and item.id not in archive_ids:
            archive_ids.add(item.id)
            group.archives.append(item)

    def add_submission(item: Optional[ArchiveSubmission]) -> None:
        if item and item.id is not None and item.id not in submission_ids:
            submission_ids.add(item.id)
            group.submissions.append(item)

    add_archive(archive)
    add_submission(submission)

    linked_archive = archive
    if submission and submission.created_archive_id:
        linked_archive = await db.get(Archive, submission.created_archive_id)
        if linked_archive:
            add_archive(linked_archive)
        else:
            group.warnings.append(f"關聯考古題 #{submission.created_archive_id} 已不存在")

    for item in list(group.archives):
        siblings = (
            await db.execute(
                select(ArchiveSubmission).where(ArchiveSubmission.created_archive_id == item.id)
            )
        ).scalars().all()
        for sibling in siblings:
            add_submission(sibling)

    if linked_archive and not archive:
        add_archive(linked_archive)

    return group


def _soft_delete_archive(archive: Archive, *, now: datetime, user_id: Optional[int], reason: str) -> bool:
    if archive.deleted_at is not None:
        return False
    archive.deleted_at = now
    archive.deleted_by_id = user_id
    archive.deleted_reason = reason
    archive.restored_at = None
    archive.restored_by_id = None
    return True


def _soft_delete_submission(
    submission: ArchiveSubmission,
    *,
    now: datetime,
    user_id: Optional[int],
    reason: str,
) -> bool:
    if is_archive_submission_trashed(submission):
        return False
    submission.status = SubmissionStatus.DELETED
    submission.deleted_at = now
    submission.deleted_by_id = user_id
    submission.delete_reason = reason
    submission.lifecycle_reason = None
    submission.restored_at = None
    submission.restored_by_id = None
    return True


def _temporarily_takedown_submission(
    submission: ArchiveSubmission,
    *,
    reason: str,
    reviewer_id: Optional[int],
    now: datetime,
) -> bool:
    if is_archive_submission_trashed(submission):
        return False
    if submission.status == SubmissionStatus.TAKEDOWN:
        return False
    submission.status = SubmissionStatus.TAKEDOWN
    submission.lifecycle_reason = reason
    submission.reviewer_id = reviewer_id
    submission.reviewed_at = now
    return True


async def soft_delete_archive_with_submission_takedown(
    db: SQLModelAsyncSession,
    *,
    archive: Archive,
    user_id: Optional[int],
    reason: str,
    now: Optional[datetime] = None,
) -> dict:
    timestamp = now or datetime.now(timezone.utc)
    archive_count = 1 if _soft_delete_archive(archive, now=timestamp, user_id=user_id, reason=reason) else 0
    submissions = (
        await db.execute(
            select(ArchiveSubmission).where(
                ArchiveSubmission.created_archive_id == archive.id,
                ArchiveSubmission.deleted_at.is_(None),
                ArchiveSubmission.status != SubmissionStatus.DELETED,
            )
        )
    ).scalars().all()
    submission_count = sum(
        1
        for item in submissions
        if _temporarily_takedown_submission(
            item,
            reason=LIFECYCLE_ARCHIVE_TRASHED,
            reviewer_id=user_id,
            now=timestamp,
        )
    )
    return {"archives": archive_count, "submissions_takedown": submission_count, "warnings": []}


async def soft_delete_submission_with_linked_archive(
    db: SQLModelAsyncSession,
    *,
    submission: ArchiveSubmission,
    user_id: Optional[int],
    reason: str,
    now: Optional[datetime] = None,
) -> dict:
    timestamp = now or datetime.now(timezone.utc)
    submission_count = 1 if _soft_delete_submission(submission, now=timestamp, user_id=user_id, reason=reason) else 0
    archive_count = 0
    warnings: list[str] = []
    if submission.created_archive_id:
        archive = await db.get(Archive, submission.created_archive_id)
        if archive:
            archive_count = 1 if _soft_delete_archive(archive, now=timestamp, user_id=user_id, reason=reason) else 0
        else:
            warnings.append(f"關聯考古題 #{submission.created_archive_id} 已不存在")
    return {"archives": archive_count, "submissions": submission_count, "warnings": warnings}


async def restore_archive_with_temporary_submissions(
    db: SQLModelAsyncSession,
    *,
    archive: Archive,
    user_id: Optional[int],
    now: Optional[datetime] = None,
) -> dict:
    timestamp = now or datetime.now(timezone.utc)
    restored_archives = 0
    if archive.deleted_at is not None:
        archive.deleted_at = None
        archive.deleted_by_id = None
        archive.deleted_reason = None
        archive.restored_at = timestamp
        archive.restored_by_id = user_id
        restored_archives = 1

    submissions = (
        await db.execute(
            select(ArchiveSubmission).where(
                ArchiveSubmission.created_archive_id == archive.id,
                ArchiveSubmission.status == SubmissionStatus.TAKEDOWN,
                ArchiveSubmission.lifecycle_reason == LIFECYCLE_ARCHIVE_TRASHED,
            )
        )
    ).scalars().all()
    for item in submissions:
        item.status = SubmissionStatus.APPROVED
        item.lifecycle_reason = None
        item.reviewer_id = user_id
        item.reviewed_at = timestamp

    return {"archives": restored_archives, "submissions_restored": len(submissions), "warnings": []}


async def mark_linked_submissions_archive_permanently_deleted(
    db: SQLModelAsyncSession,
    *,
    archive: Archive,
    user_id: Optional[int],
    now: Optional[datetime] = None,
) -> int:
    timestamp = now or datetime.now(timezone.utc)
    submissions = (
        await db.execute(
            select(ArchiveSubmission).where(ArchiveSubmission.created_archive_id == archive.id)
        )
    ).scalars().all()
    for item in submissions:
        item.status = SubmissionStatus.DELETED
        item.deleted_at = item.deleted_at or timestamp
        item.deleted_by_id = item.deleted_by_id or user_id
        item.delete_reason = "linked archive permanently deleted"
        item.lifecycle_reason = LIFECYCLE_LINKED_ARCHIVE_PERMANENTLY_DELETED
        item.created_archive_id = None
        item.restored_at = None
        item.restored_by_id = None
        item.reviewed_at = timestamp
        item.reviewer_id = user_id
    return len(submissions)


async def soft_delete_archive_submission_group(
    db: SQLModelAsyncSession,
    *,
    archive: Optional[Archive] = None,
    submission: Optional[ArchiveSubmission] = None,
    user_id: Optional[int],
    reason: str,
    now: Optional[datetime] = None,
) -> dict:
    timestamp = now or datetime.now(timezone.utc)
    group = await collect_archive_submission_group(db, archive=archive, submission=submission)
    archive_count = sum(
        1 for item in group.archives if _soft_delete_archive(item, now=timestamp, user_id=user_id, reason=reason)
    )
    submission_count = sum(
        1
        for item in group.submissions
        if _soft_delete_submission(item, now=timestamp, user_id=user_id, reason=reason)
    )
    return {
        "archives": archive_count,
        "submissions": submission_count,
        "warnings": group.warnings,
    }


async def restore_archive_submission_group(
    db: SQLModelAsyncSession,
    *,
    archive: Optional[Archive] = None,
    submission: Optional[ArchiveSubmission] = None,
    user_id: Optional[int],
    now: Optional[datetime] = None,
) -> dict:
    timestamp = now or datetime.now(timezone.utc)
    group = await collect_archive_submission_group(db, archive=archive, submission=submission)
    restored_archives = 0
    restored_submissions = 0

    for item in group.archives:
        if item.deleted_at is None:
            continue
        item.deleted_at = None
        item.deleted_by_id = None
        item.deleted_reason = None
        item.restored_at = timestamp
        item.restored_by_id = user_id
        restored_archives += 1

    for item in group.submissions:
        if not is_archive_submission_trashed(item):
            continue
        item.deleted_at = None
        item.deleted_by_id = None
        item.delete_reason = None
        item.lifecycle_reason = None
        item.restored_at = timestamp
        item.restored_by_id = user_id
        item.status = SubmissionStatus.APPROVED if item.created_archive_id else SubmissionStatus.PENDING
        if item.created_archive_id:
            item.reviewed_at = timestamp
            item.reviewer_id = user_id
        restored_submissions += 1

    return {
        "archives": restored_archives,
        "submissions": restored_submissions,
        "warnings": group.warnings,
    }


async def _count_rows(db: SQLModelAsyncSession, statement) -> int:
    result = await db.execute(statement)
    return int(result.scalar() or 0)


async def _remove_storage_object_if_unreferenced(
    db: SQLModelAsyncSession,
    object_name: Optional[str],
    warnings: list[str],
    *,
    exclude_archive_ids: Optional[set[int]] = None,
    exclude_submission_ids: Optional[set[int]] = None,
) -> int:
    if not object_name:
        return 0

    exclude_archive_ids = exclude_archive_ids or set()
    exclude_submission_ids = exclude_submission_ids or set()

    archive_query = select(func.count(Archive.id)).where(Archive.object_name == object_name)
    live_archive_query = archive_query.where(Archive.deleted_at.is_(None))
    if exclude_archive_ids:
        archive_query = archive_query.where(~Archive.id.in_(exclude_archive_ids))
        live_archive_query = live_archive_query.where(~Archive.id.in_(exclude_archive_ids))

    submission_query = select(func.count(ArchiveSubmission.id)).where(ArchiveSubmission.object_name == object_name)
    live_submission_query = submission_query.where(
        ArchiveSubmission.deleted_at.is_(None),
        ArchiveSubmission.status != SubmissionStatus.DELETED,
    )
    if exclude_submission_ids:
        submission_query = submission_query.where(~ArchiveSubmission.id.in_(exclude_submission_ids))
        live_submission_query = live_submission_query.where(~ArchiveSubmission.id.in_(exclude_submission_ids))

    live_refs = await _count_rows(db, live_archive_query) + await _count_rows(db, live_submission_query)
    all_refs = await _count_rows(db, archive_query) + await _count_rows(db, submission_query)
    if live_refs:
        warnings.append(f"Storage object kept because live records still reference it: {object_name}")
        return 0
    if all_refs:
        warnings.append(f"Storage object kept because other trashed records still reference it: {object_name}")
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


async def hard_delete_archive_submission_group(
    db: SQLModelAsyncSession,
    *,
    archive: Optional[Archive] = None,
    submission: Optional[ArchiveSubmission] = None,
    warnings: list[str],
) -> dict:
    group = await collect_archive_submission_group(db, archive=archive, submission=submission)
    group.warnings.extend(warnings)
    timestamp = datetime.now(timezone.utc)

    for item in group.archives:
        _soft_delete_archive(item, now=timestamp, user_id=item.deleted_by_id, reason=item.deleted_reason or "group hard delete")
    for item in group.submissions:
        _soft_delete_submission(item, now=timestamp, user_id=item.deleted_by_id, reason=item.delete_reason or "group hard delete")

    archive_ids = {item.id for item in group.archives if item.id is not None}
    submission_ids = {item.id for item in group.submissions if item.id is not None}
    object_names = {item.object_name for item in [*group.archives, *group.submissions] if item.object_name}

    deleted_objects = 0
    for object_name in object_names:
        deleted_objects += await _remove_storage_object_if_unreferenced(
            db,
            object_name,
            group.warnings,
            exclude_archive_ids=archive_ids,
            exclude_submission_ids=submission_ids,
        )

    messages = []
    if archive_ids:
        messages = (
            await db.execute(
                select(ArchiveDiscussionMessage).where(ArchiveDiscussionMessage.archive_id.in_(archive_ids))
            )
        ).scalars().all()

    for item in group.submissions:
        await db.delete(item)
    for message in messages:
        await db.delete(message)
    for item in group.archives:
        await db.delete(item)

    warnings[:] = group.warnings
    archive_count = len(group.archives)
    submission_count = len(group.submissions)
    return {
        "type": "archive_submission_group",
        "id": archive.id if archive else submission.id if submission else None,
        "name": archive.name if archive else f"{submission.subject} / {submission.name}" if submission else "archive group",
        "deletedChildren": {
            "archives": archive_count,
            "linkedSubmissionsDeleted": submission_count,
            "comments": len(messages),
            "files": deleted_objects,
        },
        "deleted": archive_count + submission_count + len(messages),
        "message": f"已永久刪除考古題與 {submission_count} 筆關聯投稿，並清除相關檔案。",
    }
