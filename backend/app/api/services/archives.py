import io
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
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
from app.utils.auth import get_current_user
from app.utils.storage import get_minio_client

router = APIRouter()


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

    await _ensure_category(db, category)

    course = None
    if current_user.is_admin:
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
                requester_id=current_user.user_id,
            )
            db.add(submission)
            await db.commit()
            await db.refresh(submission)

            return {
                "success": True,
                "message": "File submitted for review",
                "submission": {
                    "id": submission.id,
                    "name": submission.name,
                    "professor": submission.professor,
                    "archive_type": submission.archive_type,
                    "has_answers": submission.has_answers,
                    "status": submission.status,
                    "created_at": submission.created_at,
                    "file_size": file_size,
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

        return {
            "success": True,
            "message": "File uploaded successfully",
            "archive": {
                "id": archive.id,
                "name": archive.name,
                "professor": archive.professor,
                "archive_type": archive.archive_type,
                "has_answers": archive.has_answers,
                "created_at": archive.created_at,
                "file_size": file_size,
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
    return result.scalars().all()


@router.get("/admin/submissions", response_model=list[ArchiveSubmissionRead])
async def list_archive_submissions_for_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(
        select(ArchiveSubmission).order_by(
            ArchiveSubmission.status.asc(),
            ArchiveSubmission.created_at.desc(),
        )
    )
    return result.scalars().all()


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
    if submission.status != SubmissionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submission already reviewed")

    if submission_data.subject is not None:
        submission.subject = submission_data.subject
    if submission_data.category is not None:
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

    await db.commit()
    await db.refresh(submission)
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
    if submission.status != SubmissionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submission already reviewed")

    course = (
        await db.execute(
            select(Course).where(
                Course.name == submission.subject,
                Course.category == submission.category,
                Course.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()

    if not course:
        course = Course(name=submission.subject, category=submission.category)
        db.add(course)
        await db.commit()
        await db.refresh(course)

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
    if submission.status != SubmissionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submission already reviewed")

    submission.status = SubmissionStatus.REJECTED
    submission.reviewer_id = current_user.user_id
    submission.review_note = decision.note if decision else None
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(submission)
    return submission
