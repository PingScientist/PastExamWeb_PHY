import io
import os
import re
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, text
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.models import (
    Archive,
    ArchiveSubmission,
    ArchiveSubmissionRead,
    ArchiveSubmissionUpdate,
    Course,
    CourseCategoryConfig,
    SubmissionDecision,
    SubmissionStatus,
    User,
)
from app.api.services.archive_submission_lifecycle import (
    LIFECYCLE_ARCHIVE_TRASHED,
    LIFECYCLE_COURSE_TRASHED,
    LIFECYCLE_LINKED_ARCHIVE_PERMANENTLY_DELETED,
    soft_delete_submission_with_linked_archive,
)
from app.utils.auth import get_current_user
from app.utils.storage import get_minio_client

router = APIRouter()
logger = logging.getLogger(__name__)


async def _ensure_category(db: AsyncSession, category_key: str) -> None:
    result = await db.execute(
        select(CourseCategoryConfig).where(
            CourseCategoryConfig.key == category_key,
            CourseCategoryConfig.is_active.is_(True),
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course category does not exist",
        )


def _normalize_category_key(value: str) -> str:
    key = (value or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9-]{2,40}", key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category key must use lowercase letters, numbers, or hyphens",
        )
    return key


def _unwrap_form_default(value, default=None):
    if hasattr(value, "default"):
        return default if value.default is Ellipsis else value.default
    return value


def _normalize_submission_status(raw_status):
    if raw_status is None:
        return None

    value = raw_status.value if hasattr(raw_status, "value") else raw_status
    normalized = str(value).strip().lower()
    status_by_value = {
        "pending": SubmissionStatus.PENDING,
        "approved": SubmissionStatus.APPROVED,
        "rejected": SubmissionStatus.REJECTED,
        "deleted": SubmissionStatus.DELETED,
        "takedown": SubmissionStatus.TAKEDOWN,
    }
    normalized_status = status_by_value.get(normalized)
    if normalized_status is None:
        logger.warning("Unsupported submission status encountered: %s", value)
    return normalized_status


def _is_admin_upload_submission(submission_data) -> bool:
    flag = getattr(submission_data, "is_admin_upload", None)
    if isinstance(submission_data, dict):
        flag = submission_data.get("is_admin_upload")
    review_note = getattr(submission_data, "review_note", None)
    if isinstance(submission_data, dict):
        review_note = submission_data.get("review_note")
    return bool(flag) or str(review_note or "").strip().lower() in {"管理員上傳", "admin upload"}


async def _ensure_or_create_requested_category(
    db: AsyncSession,
    key: str,
    name: str | None,
    label: str | None,
    icon: str | None,
) -> CourseCategoryConfig:
    category_key = _normalize_category_key(key)
    result = await db.execute(
        select(CourseCategoryConfig).where(CourseCategoryConfig.key == category_key)
    )
    category = result.scalar_one_or_none()
    if category:
        if not category.is_active:
            category.is_active = True
        return category

    max_order = (
        await db.execute(select(func.max(CourseCategoryConfig.order_index)))
    ).scalar_one_or_none()
    category = CourseCategoryConfig(
        key=category_key,
        name=(name or category_key).strip(),
        label=(label or name or category_key).strip(),
        icon=(icon or "pi pi-fw pi-book").strip(),
        order_index=(max_order or 0) + 1,
        is_active=True,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.post("/upload")
async def upload_archive(
    file: UploadFile,
    subject: str = Form(...),
    category: str = Form(...),
    professor: str = Form(...),
    archive_type: str = Form(...),
    has_answers: bool = Form(False),
    filename: str = Form(...),
    academic_year: int = Form(...),
    request_new_course: bool = Form(False),
    request_new_category: bool = Form(False),
    requested_course_name: str | None = Form(None),
    requested_category_key: str | None = Form(None),
    requested_category_name: str | None = Form(None),
    requested_category_label: str | None = Form(None),
    requested_category_icon: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Upload a new archive and create course if not exists
    """
    user_query = select(User).where(
        User.id == current_user.user_id, User.deleted_at.is_(None)
    )
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    request_new_course = bool(_unwrap_form_default(request_new_course, False))
    request_new_category = bool(_unwrap_form_default(request_new_category, False))
    requested_course_name = _unwrap_form_default(requested_course_name)
    requested_category_key = _unwrap_form_default(requested_category_key)
    requested_category_name = _unwrap_form_default(requested_category_name)
    requested_category_label = _unwrap_form_default(requested_category_label)
    requested_category_icon = _unwrap_form_default(requested_category_icon)

    subject = subject.strip()
    category = category.strip()
    professor = professor.strip()
    requested_course_name = (requested_course_name or "").strip() or None
    requested_category_key = (requested_category_key or "").strip() or None
    requested_category_name = (requested_category_name or "").strip() or None
    requested_category_label = (requested_category_label or "").strip() or None
    requested_category_icon = (requested_category_icon or "").strip() or None

    if request_new_category:
        if not requested_category_key or not requested_category_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New category key and name are required",
            )
        category = _normalize_category_key(requested_category_key)
        requested_category_key = category
        if not requested_course_name:
            requested_course_name = subject
        request_new_course = True
    else:
        await _ensure_category(db, category)

    if request_new_course:
        if not requested_course_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New course name is required",
            )
        subject = requested_course_name

    course = None
    if current_user.is_admin:
        if request_new_category:
            await _ensure_or_create_requested_category(
                db,
                requested_category_key,
                requested_category_name,
                requested_category_label,
                requested_category_icon,
            )
        query = select(Course).where(
            Course.name == subject,
            Course.category == category,
            Course.deleted_at.is_(None),
        )
        result = await db.execute(query)
        course = result.scalar_one_or_none()

        if not course:
            course = Course(name=subject, category=category)
            db.add(course)
            await db.commit()
            await db.refresh(course)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed"
        )

    file_content = await file.read()
    file_size = len(file_content)

    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit",
        )

    _, file_extension = os.path.splitext(file.filename)
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    if current_user.is_admin:
        object_name = f"archives/{course.id}/{unique_filename}"
    else:
        object_name = f"archive-submissions/{current_user.user_id}/{unique_filename}"

    try:
        minio_client = get_minio_client()
        file_data = io.BytesIO(file_content)

        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=object_name,
            data=file_data,
            length=file_size,
            content_type="application/pdf",
        )

        if not current_user.is_admin:
            submission = ArchiveSubmission(
                subject=subject,
                category=category,
                name=filename,
                professor=professor,
                archive_type=archive_type,
                has_answers=has_answers,
                object_name=object_name,
                academic_year=academic_year,
                requested_course_name=requested_course_name if request_new_course else None,
                requested_category_key=requested_category_key if request_new_category else None,
                requested_category_name=requested_category_name if request_new_category else None,
                requested_category_label=requested_category_label if request_new_category else None,
                requested_category_icon=requested_category_icon if request_new_category else None,
                requester_id=current_user.user_id,
            )
            db.add(submission)
            await db.commit()
            await db.refresh(submission)

            return {
                "success": True,
                "message": "File submitted for review",
                "is_admin_upload": False,
                "submission": {
                    "id": submission.id,
                    "name": submission.name,
                    "professor": submission.professor,
                    "archive_type": submission.archive_type,
                    "has_answers": submission.has_answers,
                    "status": submission.status,
                    "created_at": submission.created_at,
                    "file_size": file_size,
                    "is_admin_upload": False,
                },
            }

        archive = Archive(
            course_id=course.id,
            name=filename,
            professor=professor,
            archive_type=archive_type,
            has_answers=has_answers,
            object_name=object_name,
            academic_year=academic_year,
            uploader_id=current_user.user_id,
        )
        db.add(archive)
        await db.commit()
        await db.refresh(archive)

        submission = ArchiveSubmission(
            subject=subject,
            category=category,
            name=filename,
            professor=professor,
            archive_type=archive_type,
            has_answers=has_answers,
            object_name=object_name,
            academic_year=academic_year,
            requested_course_name=requested_course_name if request_new_course else None,
            requested_category_key=requested_category_key if request_new_category else None,
            requested_category_name=requested_category_name if request_new_category else None,
            requested_category_label=requested_category_label if request_new_category else None,
            requested_category_icon=requested_category_icon if request_new_category else None,
            status=SubmissionStatus.APPROVED,
            requester_id=current_user.user_id,
            reviewer_id=current_user.user_id,
            is_admin_upload=True,
            created_archive_id=archive.id,
            reviewed_at=datetime.now(timezone.utc),
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)

        return {
            "success": True,
            "message": "File uploaded successfully",
            "is_admin_upload": True,
            "archive": {
                "id": archive.id,
                "name": archive.name,
                "professor": archive.professor,
                "archive_type": archive.archive_type,
                "has_answers": archive.has_answers,
                "created_at": archive.created_at,
                "file_size": file_size,
            },
            "submission": {
                "id": submission.id,
                "name": submission.name,
                "professor": submission.professor,
                "archive_type": submission.archive_type,
                "has_answers": submission.has_answers,
                "status": submission.status,
                "created_at": submission.created_at,
                "file_size": file_size,
                "is_admin_upload": True,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get("/submissions/me", response_model=list[ArchiveSubmissionRead])
async def list_my_archive_submissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(ArchiveSubmission)
        .where(ArchiveSubmission.requester_id == current_user.user_id)
        .order_by(ArchiveSubmission.created_at.desc())
    )
    return [
        ArchiveSubmissionRead.model_validate(submission).model_copy(
            update={"is_admin_upload": _is_admin_upload_submission(submission)}
        )
        for submission in result.scalars().all()
    ]


@router.delete("/submissions/{submission_id}")
async def delete_my_archive_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    if submission.deleted_at is not None or submission.status == SubmissionStatus.DELETED:
        return {"success": True, "id": submission.id}

    is_owner = submission.requester_id == current_user.user_id or (
        submission.owner_id is not None and submission.owner_id == current_user.user_id
    )
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if submission.status != SubmissionStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved submissions can be deleted by users",
        )

    result = await soft_delete_submission_with_linked_archive(
        db,
        submission=submission,
        user_id=current_user.user_id,
        reason="user deleted",
    )

    await db.commit()

    return {
        "success": True,
        "id": submission.id,
        "status": submission.status,
        "deleted": result,
        "message": "已刪除，管理員可於垃圾桶中恢復",
    }


@router.get("/admin/submissions", response_model=list[ArchiveSubmissionRead])
async def list_archive_submissions_for_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(
        text("""
            SELECT
                archive_submissions.id,
                archive_submissions.subject,
                archive_submissions.category,
                archive_submissions.name,
                archive_submissions.academic_year,
                LOWER(CAST(archive_submissions.archive_type AS TEXT)) AS archive_type,
                archive_submissions.professor,
                archive_submissions.has_answers,
                archive_submissions.requested_course_name,
                archive_submissions.requested_category_key,
                archive_submissions.requested_category_name,
                archive_submissions.requested_category_label,
                archive_submissions.requested_category_icon,
                LOWER(CAST(archive_submissions.status AS TEXT)) AS status,
                archive_submissions.requester_id,
                archive_submissions.reviewer_id,
                archive_submissions.review_note,
                (
                    archive_submissions.is_admin_upload
                    OR LOWER(TRIM(COALESCE(archive_submissions.review_note, ''))) IN ('管理員上傳', 'admin upload')
                ) AS is_admin_upload,
                archive_submissions.created_archive_id,
                archive_submissions.lifecycle_reason,
                (archives.deleted_at IS NOT NULL) AS linked_archive_deleted,
                (courses.deleted_at IS NOT NULL) AS linked_course_deleted,
                archive_submissions.created_at,
                archive_submissions.reviewed_at,
                users.name AS requester_name,
                users.email AS requester_email
            FROM archive_submissions
            LEFT JOIN users
                ON users.id = archive_submissions.requester_id
            LEFT JOIN archives
                ON archives.id = archive_submissions.created_archive_id
            LEFT JOIN courses
                ON courses.id = archives.course_id
            ORDER BY
                CASE LOWER(CAST(archive_submissions.status AS TEXT))
                    WHEN 'pending' THEN 1
                    WHEN 'approved' THEN 2
                    WHEN 'rejected' THEN 3
                    WHEN 'takedown' THEN 4
                    WHEN 'deleted' THEN 5
                    ELSE 99
                END,
                archive_submissions.created_at DESC
        """)
    )
    archive_submissions = []
    skipped_submission_count = 0
    for row in result.all():
        row_dict = dict(row._mapping)
        normalized_status = _normalize_submission_status(row_dict.get("status"))
        if normalized_status is None:
            skipped_submission_count += 1
            continue

        row_dict["status"] = normalized_status
        try:
            row_dict["is_admin_upload"] = bool(row_dict.get("is_admin_upload"))
            archive_submissions.append(ArchiveSubmissionRead.model_validate(row_dict))
        except Exception as exc:
            skipped_submission_count += 1
            logger.warning(
                "Skipping archive submission %s due to invalid payload: %s",
                row_dict.get("id"),
                exc,
            )

    if skipped_submission_count:
        logger.info(
            "Skipped %s archive submissions in admin list due to unsupported/invalid status",
            skipped_submission_count,
        )
    return archive_submissions


@router.get("/admin/submissions/{submission_id}/preview-file")
async def get_archive_submission_preview_file(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    try:
        response = get_minio_client().get_object(
            settings.MINIO_BUCKET_NAME,
            submission.object_name,
        )
        data = response.read()
        response.close()
        response.release_conn()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load submission preview file: {exc}",
        )

    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{submission.name}.pdf"',
            "Cache-Control": "no-store",
        },
    )


@router.put("/admin/submissions/{submission_id}", response_model=ArchiveSubmissionRead)
async def update_archive_submission_for_admin(
    submission_id: int,
    submission_data: ArchiveSubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    if submission_data.subject is not None:
        submission.subject = submission_data.subject
    if submission_data.category is not None:
        if not (submission_data.requested_category_key or submission.requested_category_key):
            await _ensure_category(db, submission_data.category)
        submission.category = submission_data.category
    if submission_data.name is not None:
        submission.name = submission_data.name
    if submission_data.academic_year is not None:
        submission.academic_year = submission_data.academic_year
    if submission_data.archive_type is not None:
        submission.archive_type = submission_data.archive_type
    if submission_data.professor is not None:
        submission.professor = submission_data.professor
    if submission_data.has_answers is not None:
        submission.has_answers = submission_data.has_answers
    if submission_data.requested_course_name is not None:
        submission.requested_course_name = submission_data.requested_course_name.strip() or None
    if submission_data.requested_category_key is not None:
        key = submission_data.requested_category_key.strip()
        submission.requested_category_key = _normalize_category_key(key) if key else None
    if submission_data.requested_category_name is not None:
        submission.requested_category_name = submission_data.requested_category_name.strip() or None
    if submission_data.requested_category_label is not None:
        submission.requested_category_label = submission_data.requested_category_label.strip() or None
    if submission_data.requested_category_icon is not None:
        submission.requested_category_icon = submission_data.requested_category_icon.strip() or None

    await db.commit()
    await db.refresh(submission)

    if submission.created_archive_id:
        course_name = submission.requested_course_name or submission.subject
        category_key = submission.requested_category_key or submission.category
        if submission.requested_category_key:
            await _ensure_or_create_requested_category(
                db,
                submission.requested_category_key,
                submission.requested_category_name,
                submission.requested_category_label,
                submission.requested_category_icon,
            )
        else:
            await _ensure_category(db, category_key)

        course = (
            await db.execute(
                select(Course).where(
                    Course.name == course_name,
                    Course.category == category_key,
                    Course.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if not course:
            course = Course(name=course_name, category=category_key)
            db.add(course)
            await db.commit()
            await db.refresh(course)

        archive = await db.get(Archive, submission.created_archive_id)
        if archive:
            archive.course_id = course.id
            archive.name = submission.name
            archive.academic_year = submission.academic_year
            archive.archive_type = submission.archive_type
            archive.professor = submission.professor
            archive.has_answers = submission.has_answers
            archive.updated_at = datetime.now(timezone.utc)
            db.add(archive)
            await db.commit()

    return submission


@router.post("/admin/submissions/{submission_id}/approve", response_model=ArchiveSubmissionRead)
async def approve_archive_submission(
    submission_id: int,
    decision: SubmissionDecision | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    course_name = submission.requested_course_name or submission.subject
    category_key = submission.requested_category_key or submission.category

    if submission.requested_category_key:
        await _ensure_or_create_requested_category(
            db,
            submission.requested_category_key,
            submission.requested_category_name,
            submission.requested_category_label,
            submission.requested_category_icon,
        )
    else:
        await _ensure_category(db, category_key)

    course = (
        await db.execute(
            select(Course).where(
                Course.name == course_name,
                Course.category == category_key,
                Course.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()

    if not course:
        course = Course(name=course_name, category=category_key)
        db.add(course)
        await db.commit()
        await db.refresh(course)

    archive = await db.get(Archive, submission.created_archive_id) if submission.created_archive_id else None
    if archive:
        archive.course_id = course.id
        archive.name = submission.name
        archive.academic_year = submission.academic_year
        archive.archive_type = submission.archive_type
        archive.professor = submission.professor
        archive.has_answers = submission.has_answers
        archive.object_name = submission.object_name
        archive.uploader_id = submission.requester_id
        archive.deleted_at = None
        archive.updated_at = datetime.now(timezone.utc)
    else:
        archive = Archive(
            course_id=course.id,
            name=submission.name,
            academic_year=submission.academic_year,
            archive_type=submission.archive_type,
            professor=submission.professor,
            has_answers=submission.has_answers,
            object_name=submission.object_name,
            uploader_id=submission.requester_id,
        )
    db.add(archive)
    await db.commit()
    await db.refresh(archive)

    submission.status = SubmissionStatus.APPROVED
    submission.reviewer_id = current_user.user_id
    submission.review_note = decision.note if decision else None
    submission.created_archive_id = archive.id
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.post("/admin/submissions/{submission_id}/reject", response_model=ArchiveSubmissionRead)
async def reject_archive_submission(
    submission_id: int,
    decision: SubmissionDecision | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    submission.status = SubmissionStatus.REJECTED
    submission.reviewer_id = current_user.user_id
    submission.review_note = decision.note if decision else None
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.post("/admin/submissions/{submission_id}/takedown", response_model=ArchiveSubmissionRead)
async def takedown_archive_submission(
    submission_id: int,
    decision: SubmissionDecision | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    normalized_status = _normalize_submission_status(submission.status)
    if normalized_status in {SubmissionStatus.DELETED, SubmissionStatus.TAKEDOWN}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission cannot be taken down from its current status",
        )

    submission.status = SubmissionStatus.TAKEDOWN
    submission.reviewer_id = current_user.user_id
    submission.review_note = decision.note if decision else submission.review_note
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.post("/admin/submissions/{submission_id}/republish", response_model=ArchiveSubmissionRead)
async def republish_archive_submission(
    submission_id: int,
    decision: SubmissionDecision | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    normalized_status = _normalize_submission_status(submission.status)
    if normalized_status != SubmissionStatus.TAKEDOWN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only taken down submissions can be republished",
        )

    if submission.lifecycle_reason == LIFECYCLE_LINKED_ARCHIVE_PERMANENTLY_DELETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="無法復原：關聯考古題已永久刪除",
        )

    if submission.lifecycle_reason == LIFECYCLE_ARCHIVE_TRASHED and submission.created_archive_id:
        archive = await db.get(Archive, submission.created_archive_id)
        if archive and archive.deleted_at is not None:
            course = await db.get(Course, archive.course_id)
            if not course or course.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="無法重新上架，請先至垃圾桶復原原課程",
                )
            archive.deleted_at = None
            archive.deleted_by_id = None
            archive.deleted_reason = None
            archive.restored_at = datetime.now(timezone.utc)
            archive.restored_by_id = current_user.user_id

    if submission.lifecycle_reason == LIFECYCLE_COURSE_TRASHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="無法重新上架，請先至垃圾桶復原原課程",
        )

    submission.status = SubmissionStatus.APPROVED
    submission.lifecycle_reason = None
    submission.reviewer_id = current_user.user_id
    submission.review_note = decision.note if decision else submission.review_note
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.delete("/admin/submissions/{submission_id}")
async def delete_archive_submission_for_admin(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(ArchiveSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    if submission.deleted_at is not None or submission.status == SubmissionStatus.DELETED:
        return {"success": True}

    result = await soft_delete_submission_with_linked_archive(
        db,
        submission=submission,
        user_id=current_user.user_id,
        reason="admin deleted",
    )
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True, "id": submission.id, "deleted": result}
