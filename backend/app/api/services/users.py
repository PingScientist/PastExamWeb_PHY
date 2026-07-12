from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.models.models import (
    ArchiveSubmission,
    SubmissionStatus,
    User,
    UserCreate,
    UserPasswordResetRequest,
    UserNicknameUpdate,
    UserRead,
    UserRoles,
    UserSubmissionStatsRead,
    UserSubmissionRecordRead,
    UserSubmissionStatusCounts,
    UserUpdate,
)
from app.utils.auth import get_current_user, get_password_hash

router = APIRouter()

NICKNAME_MAX_LENGTH = 15
USER_PASSWORD_MIN_LENGTH = 8
ONLINE_STATUS_MINUTES = 5


def _normalize_timestamp(dt: datetime | None) -> datetime | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _is_activity_recent(activity_at: datetime | None, now_utc: datetime) -> bool:
    if not activity_at:
        return False
    cutoff = now_utc - timedelta(minutes=ONLINE_STATUS_MINUTES)
    return activity_at >= cutoff


def _get_user_online_status(user: User):
    now_utc = datetime.now(timezone.utc)
    last_seen = _normalize_timestamp(getattr(user, "last_seen_at", None))
    last_login = _normalize_timestamp(user.last_login)
    last_logout = _normalize_timestamp(user.last_logout)

    if not last_login and not last_seen:
        return False, "從未登入"

    reference_time = last_seen or last_login

    if not reference_time:
        return False, "離線"

    if last_logout and reference_time and last_logout >= reference_time:
        return False, "離線"

    is_online = _is_activity_recent(reference_time, now_utc)
    return is_online, "在線" if is_online else "離線"


def _to_user_read(user: User, contributor_experience: int = 0) -> UserRead:
    is_online, status_label = _get_user_online_status(user)
    return UserRead(
        id=user.id,
        email=user.email,
        name=user.name,
        nickname=user.nickname,
        is_admin=user.is_admin,
        is_local=user.is_local,
        last_login=user.last_login,
        last_login_at=user.last_login,
        last_seen_at=user.last_seen_at,
        last_logout_at=user.last_logout,
        is_online=is_online,
        online_status_label=status_label,
        contributor_experience=contributor_experience,
    )


@router.get("/admin/users", response_model=List[UserRead])
async def get_users(
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all users (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    result = await db.execute(select(User).where(User.deleted_at.is_(None)))
    users = result.scalars().all()
    experience_result = await db.execute(
        select(ArchiveSubmission.requester_id, func.count(ArchiveSubmission.id))
        .where(
            ArchiveSubmission.status.in_(
                [SubmissionStatus.APPROVED, SubmissionStatus.TAKEDOWN]
            )
        )
        .group_by(ArchiveSubmission.requester_id)
    )
    experience_by_user = {
        requester_id: int(experience) for requester_id, experience in experience_result.all()
    }
    return [_to_user_read(user, experience_by_user.get(user.id, 0)) for user in users]


@router.get(
    "/admin/users/{user_id}/submission-stats",
    response_model=UserSubmissionStatsRead,
)
async def get_user_submission_stats(
    user_id: int,
    include_records: bool = False,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Return one user's archive submission status totals for administrators."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user_result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    counts_result = await db.execute(
        select(ArchiveSubmission.status, func.count(ArchiveSubmission.id))
        .where(ArchiveSubmission.requester_id == user_id)
        .group_by(ArchiveSubmission.status)
    )
    counts = {submission_status.value: 0 for submission_status in SubmissionStatus}
    for submission_status, count in counts_result.all():
        status_key = (
            submission_status.value
            if isinstance(submission_status, SubmissionStatus)
            else str(submission_status)
        )
        if status_key in counts:
            counts[status_key] = int(count)

    contributor_experience = counts[SubmissionStatus.APPROVED.value] + counts[
        SubmissionStatus.TAKEDOWN.value
    ]
    submission_records = []
    if include_records:
        records_result = await db.execute(
            select(ArchiveSubmission)
            .where(ArchiveSubmission.requester_id == user_id)
            .order_by(ArchiveSubmission.created_at.desc(), ArchiveSubmission.id.desc())
        )
        submission_records = [
            UserSubmissionRecordRead(
                id=submission.id,
                status=submission.status,
                archive_type=submission.archive_type,
                course_name=submission.requested_course_name or submission.subject,
                exam_name=submission.name,
                academic_year=submission.academic_year,
                professor=submission.professor,
                has_answers=submission.has_answers,
                requested_course_name=submission.requested_course_name,
                requested_category_key=submission.requested_category_key,
                is_admin_upload=submission.is_admin_upload,
                submitted_at=submission.created_at,
                reviewed_at=submission.reviewed_at,
                review_comment=submission.review_note,
            )
            for submission in records_result.scalars().all()
        ]
    return UserSubmissionStatsRead(
        user_id=user.id,
        name=user.name,
        contributor_experience=contributor_experience,
        total_count=sum(counts.values()),
        status_counts=UserSubmissionStatusCounts(**counts),
        records_total=len(submission_records) if include_records else sum(counts.values()),
        submission_records=submission_records,
    )


@router.post("/admin/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    payload: UserPasswordResetRequest,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Reset password for a local user (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_local:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="此帳號不是本地帳號，無法由系統重設密碼。",
        )

    new_password = payload.new_password.strip() if payload.new_password else ''

    if not new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密碼不可為空")

    if len(new_password) < USER_PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"新密碼長度至少 {USER_PASSWORD_MIN_LENGTH} 字",
        )

    user.password_hash = get_password_hash(new_password)
    await db.commit()

    return {"message": "密碼已重設"}



@router.post("/admin/users", response_model=UserRead)
async def create_user(
    user_data: UserCreate,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new user (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    result = await db.execute(select(User).where(User.name == user_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this name already exists",
        )
    hashed_password = get_password_hash(user_data.password)
    user = User(
        name=user_data.name,
        nickname=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        is_admin=user_data.is_admin,
        is_local=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    user = await db.scalar(
        select(User).where(User.id == current_user.user_id, User.deleted_at.is_(None))
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.nickname:
        user.nickname = user.name
        await db.commit()
        await db.refresh(user)
    return user


@router.patch("/me/nickname", response_model=UserRead)
async def update_my_nickname(
    payload: UserNicknameUpdate,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    user = await db.scalar(
        select(User).where(User.id == current_user.user_id, User.deleted_at.is_(None))
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    nickname = (payload.nickname or "").strip()
    if not nickname:
        nickname = user.name
    if len(nickname) > NICKNAME_MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"暱稱超出 {NICKNAME_MAX_LENGTH} 字",
        )

    user.nickname = nickname
    if payload.show_level_title is not None:
        user.show_level_title = payload.show_level_title
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/admin/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update a user (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_data.name is not None:
        result = await db.execute(
            select(User).where(User.name == user_data.name, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this name already exists",
            )
        user.name = user_data.name

    if user_data.email is not None:
        result = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        user.email = user_data.email

    if user_data.password is not None:
        user.password_hash = get_password_hash(user_data.password)

    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Delete a user (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
        )
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    return {"detail": "User deleted successfully"}
