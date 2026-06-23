import json
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.models.models import (
    Archive,
    ArchiveDiscussionMessage,
    ArchiveDiscussionMessageRead,
    ArchiveRead,
    ArchiveType,
    ArchiveUpdateCourse,
    Course,
    CourseCreate,
    CourseInfo,
    CourseRead,
    CourseReorder,
    CourseSubmission,
    CourseSubmissionCreate,
    CourseSubmissionRead,
    CoursesByCategory,
    CourseUpdate,
    SubmissionDecision,
    SubmissionStatus,
    User,
    UserRoles,
)
from app.utils.auth import get_current_user
from app.utils.auth_ws import get_ws_token_payload
from app.utils.storage import presigned_get_url

router = APIRouter()

# In-memory connection registry (single-process broadcast).
_discussion_connections_by_archive: dict[int, set[WebSocket]] = {}
DISCUSSION_MESSAGE_MAX_LENGTH = 200
CATEGORY_ORDER = {
    "freshman": 0,
    "sophomore": 1,
    "junior": 2,
    "senior": 3,
    "graduate": 4,
    "interdisciplinary": 5,
}


def _course_category_value(course: Course) -> str:
    return getattr(course.category, "value", course.category)


def _course_sort_key(course: Course) -> tuple[int, int, int]:
    category = _course_category_value(course)
    return (
        CATEGORY_ORDER.get(category, 999),
        course.order_index,
        course.id or 0,
    )


def _visible_courses(courses: list[Course]) -> list[Course]:
    seen: set[tuple[str, str]] = set()
    selected: list[Course] = []
    for course in sorted(courses, key=_course_sort_key):
        category = _course_category_value(course)
        if category not in CATEGORY_ORDER:
            continue
        key = (category, course.name)
        if key in seen:
            continue
        seen.add(key)
        selected.append(course)
    return selected


async def _next_order_index(db: AsyncSession, category) -> int:
    result = await db.execute(
        select(func.max(Course.order_index)).where(
            Course.category == category,
            Course.deleted_at.is_(None),
        )
    )
    current_max = result.scalar()
    return 0 if current_max is None else int(current_max) + 1


def _discussion_public_display_name(
    *, user_id: int, nickname: str | None, name: str | None
) -> str:
    nickname_norm = (nickname or "").strip()
    if nickname_norm:
        return nickname_norm
    return (name or "").strip()


@router.get("", response_model=CoursesByCategory)
async def get_categorized_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all courses grouped by category.
    Returns courses with their IDs grouped by category.
    """
    query = select(Course).where(Course.deleted_at.is_(None))
    result = await db.execute(query)
    courses = _visible_courses(result.scalars().all())

    categorized_courses = CoursesByCategory()
    for course in courses:
        course_info = CourseInfo(
            id=course.id,
            name=course.name,
            order_index=course.order_index,
        )
        getattr(categorized_courses, _course_category_value(course)).append(course_info)

    return categorized_courses


@router.post("/requests", response_model=CourseSubmissionRead)
async def create_course_request(
    course_data: CourseSubmissionCreate,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    existing_course = (
        await db.execute(
            select(Course).where(
                Course.name == course_data.name,
                Course.category == course_data.category,
                Course.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already exists",
        )

    existing_pending = (
        await db.execute(
            select(CourseSubmission).where(
                CourseSubmission.name == course_data.name,
                CourseSubmission.category == course_data.category,
                CourseSubmission.status == SubmissionStatus.PENDING,
            )
        )
    ).scalar_one_or_none()
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course request already pending",
        )

    if current_user.is_admin:
        course = Course(
            name=course_data.name,
            category=course_data.category,
            order_index=await _next_order_index(db, course_data.category),
        )
        db.add(course)
        await db.commit()
        await db.refresh(course)
        submission = CourseSubmission(
            name=course.name,
            category=course.category,
            requester_id=current_user.user_id,
            reviewer_id=current_user.user_id,
            status=SubmissionStatus.APPROVED,
            created_course_id=course.id,
            reviewed_at=datetime.now(timezone.utc),
        )
    else:
        submission = CourseSubmission(
            name=course_data.name,
            category=course_data.category,
            requester_id=current_user.user_id,
        )

    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/requests/me", response_model=List[CourseSubmissionRead])
async def list_my_course_requests(
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(CourseSubmission)
        .where(CourseSubmission.requester_id == current_user.user_id)
        .order_by(CourseSubmission.created_at.desc())
    )
    return result.scalars().all()


@router.get("/admin/requests", response_model=List[CourseSubmissionRead])
async def list_course_requests_for_admin(
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    result = await db.execute(
        select(CourseSubmission).order_by(
            CourseSubmission.status.asc(),
            CourseSubmission.created_at.desc(),
        )
    )
    return result.scalars().all()


@router.post("/admin/requests/{request_id}/approve", response_model=CourseSubmissionRead)
async def approve_course_request(
    request_id: int,
    decision: SubmissionDecision | None = None,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(CourseSubmission, request_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if submission.status != SubmissionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already reviewed")

    course = (
        await db.execute(
            select(Course).where(
                Course.name == submission.name,
                Course.category == submission.category,
                Course.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if not course:
        course = Course(
            name=submission.name,
            category=submission.category,
            order_index=await _next_order_index(db, submission.category),
        )
        db.add(course)
        await db.commit()
        await db.refresh(course)

    submission.status = SubmissionStatus.APPROVED
    submission.reviewer_id = current_user.user_id
    submission.review_note = decision.note if decision else None
    submission.created_course_id = course.id
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.post("/admin/requests/{request_id}/reject", response_model=CourseSubmissionRead)
async def reject_course_request(
    request_id: int,
    decision: SubmissionDecision | None = None,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    submission = await db.get(CourseSubmission, request_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if submission.status != SubmissionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already reviewed")

    submission.status = SubmissionStatus.REJECTED
    submission.reviewer_id = current_user.user_id
    submission.review_note = decision.note if decision else None
    submission.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/{course_id}/archives", response_model=List[ArchiveRead])
async def get_course_archives(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all archives for a specific course.
    """
    course_query = select(Course).where(
        Course.id == course_id, Course.deleted_at.is_(None)
    )
    result = await db.execute(course_query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found",
        )

    query = (
        select(Archive)
        .where(Archive.course_id == course_id, Archive.deleted_at.is_(None))
        .order_by(Archive.created_at.desc())
    )
    result = await db.execute(query)
    archives = result.scalars().all()

    return archives


@router.get("/{course_id}/archives/{archive_id}/preview")
async def get_archive_preview_url(
    course_id: int,
    archive_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get presigned URL for previewing an archive (30 minutes expiry)
    """
    query = select(Archive).where(
        Archive.course_id == course_id,
        Archive.id == archive_id,
        Archive.deleted_at.is_(None),
    )
    result = await db.execute(query)
    archive = result.scalar_one_or_none()

    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found"
        )

    return {
        "url": presigned_get_url(archive.object_name, expires=timedelta(minutes=30))
    }


@router.get("/{course_id}/archives/{archive_id}/download")
async def get_archive_download_url(
    course_id: int,
    archive_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get presigned URL for downloading an archive (1 hour expiry)
    This endpoint increments the download coun
    """
    query = select(Archive).where(
        Archive.course_id == course_id,
        Archive.id == archive_id,
        Archive.deleted_at.is_(None),
    )
    result = await db.execute(query)
    archive = result.scalar_one_or_none()

    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found"
        )

    archive.download_count += 1
    await db.commit()
    await db.refresh(archive)

    return {"url": presigned_get_url(archive.object_name, expires=timedelta(hours=1))}


async def _ensure_archive_exists_for_discussion(
    course_id: int, archive_id: int, db: AsyncSession
) -> Archive:
    query = select(Archive).where(
        Archive.course_id == course_id,
        Archive.id == archive_id,
        Archive.deleted_at.is_(None),
    )
    archive = (await db.execute(query)).scalar_one_or_none()
    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found"
        )
    return archive


async def _broadcast_discussion(archive_id: int, payload: dict):
    sockets = _discussion_connections_by_archive.get(archive_id)
    if not sockets:
        return

    dead: list[WebSocket] = []
    for ws in list(sockets):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)

    if dead:
        sockets = _discussion_connections_by_archive.get(archive_id)
        if sockets:
            for ws in dead:
                sockets.discard(ws)
            if not sockets:
                _discussion_connections_by_archive.pop(archive_id, None)


async def _fetch_archive_discussion_messages(
    archive_id: int,
    db: AsyncSession,
    *,
    limit: int = 50,
    before_id: int | None = None,
) -> List[ArchiveDiscussionMessageRead]:
    safe_limit = max(1, min(int(limit or 50), 100))

    stmt = (
        select(ArchiveDiscussionMessage, User.nickname, User.name)
        .join(User, User.id == ArchiveDiscussionMessage.user_id)
        .where(
            ArchiveDiscussionMessage.archive_id == archive_id,
            ArchiveDiscussionMessage.deleted_at.is_(None),
        )
        .order_by(ArchiveDiscussionMessage.id.desc())
        .limit(safe_limit)
    )
    if before_id is not None:
        stmt = stmt.where(ArchiveDiscussionMessage.id < before_id)

    rows = (await db.execute(stmt)).all()
    rows = list(reversed(rows))

    return [
        ArchiveDiscussionMessageRead(
            id=msg.id,
            archive_id=msg.archive_id,
            user_id=msg.user_id,
            user_name=_discussion_public_display_name(
                user_id=msg.user_id, nickname=nickname, name=user_name
            ),
            content=msg.content,
            created_at=msg.created_at,
        )
        for (msg, nickname, user_name) in rows
    ]


@router.get(
    "/{course_id}/archives/{archive_id}/discussion/messages",
    response_model=List[ArchiveDiscussionMessageRead],
)
async def list_archive_discussion_messages(
    course_id: int,
    archive_id: int,
    limit: int = 50,
    before_id: int | None = None,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await _ensure_archive_exists_for_discussion(course_id, archive_id, db)
    return await _fetch_archive_discussion_messages(
        archive_id,
        db,
        limit=limit,
        before_id=before_id,
    )


@router.websocket("/{course_id}/archives/{archive_id}/discussion/ws")
async def archive_discussion_ws(
    websocket: WebSocket,
    course_id: int,
    archive_id: int,
    db: AsyncSession = Depends(get_session),
):
    await websocket.accept()

    payload = await get_ws_token_payload(websocket)
    if not payload:
        await websocket.close(code=4401)
        return

    user_id = payload.get("uid")
    if not user_id:
        await websocket.close(code=4401)
        return

    user = await db.scalar(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    if not user:
        await websocket.close(code=4401)
        return

    exp = payload.get("exp")
    exp_ts = float(exp) if exp is not None else None

    try:
        await _ensure_archive_exists_for_discussion(course_id, archive_id, db)
    except HTTPException:
        await websocket.close(code=1008)
        return

    sockets = _discussion_connections_by_archive.setdefault(archive_id, set())
    sockets.add(websocket)

    try:
        history = await _fetch_archive_discussion_messages(
            archive_id, db, limit=50, before_id=None
        )
        await websocket.send_json(
            jsonable_encoder({"type": "history", "messages": history})
        )

        while True:
            raw = await websocket.receive_text()
            if exp_ts is not None and exp_ts < datetime.now(timezone.utc).timestamp():
                await websocket.close(code=4401)
                return
            try:
                data = json.loads(raw)
            except Exception:
                continue

            if not isinstance(data, dict):
                continue

            msg_type = str(data.get("type") or "").strip().lower()
            if msg_type != "send":
                continue

            raw_content = str(data.get("content") or "")
            content = raw_content.strip()
            if not content:
                continue
            if len(content) > DISCUSSION_MESSAGE_MAX_LENGTH:
                await websocket.send_json(
                    jsonable_encoder(
                        {
                            "type": "error",
                            "code": "message_too_long",
                            "detail": f"訊息超出 {DISCUSSION_MESSAGE_MAX_LENGTH} 字",
                        }
                    )
                )
                continue

            message = ArchiveDiscussionMessage(
                archive_id=archive_id,
                user_id=user.id,
                content=content,
                created_at=datetime.now(timezone.utc),
            )
            db.add(message)
            await db.commit()
            await db.refresh(message)

            # Fetch latest nickname each time (user object may be stale while WS is open).
            user_row = (
                await db.execute(
                    select(User.nickname, User.name).where(User.id == user.id)
                )
            ).one_or_none()
            latest_display_name = None
            if user_row:
                latest_display_name = _discussion_public_display_name(
                    user_id=user.id, nickname=user_row[0], name=user_row[1]
                )

            payload = jsonable_encoder(
                {
                    "type": "message",
                    "message": ArchiveDiscussionMessageRead(
                        id=message.id,
                        archive_id=message.archive_id,
                        user_id=message.user_id,
                        user_name=latest_display_name
                        or _discussion_public_display_name(
                            user_id=user.id, nickname=user.nickname, name=user.name
                        ),
                        content=message.content,
                        created_at=message.created_at,
                    ),
                }
            )
            await _broadcast_discussion(archive_id, payload)
    except WebSocketDisconnect:
        return
    finally:
        sockets = _discussion_connections_by_archive.get(archive_id)
        if sockets:
            sockets.discard(websocket)
            if not sockets:
                _discussion_connections_by_archive.pop(archive_id, None)


@router.delete("/{course_id}/archives/{archive_id}/discussion/{message_id}")
async def delete_archive_discussion_message(
    course_id: int,
    archive_id: int,
    message_id: int,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await _ensure_archive_exists_for_discussion(course_id, archive_id, db)

    message = (
        await db.execute(
            select(ArchiveDiscussionMessage).where(
                ArchiveDiscussionMessage.id == message_id,
                ArchiveDiscussionMessage.archive_id == archive_id,
                ArchiveDiscussionMessage.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    if not current_user.is_admin and message.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    message.deleted_at = datetime.now(timezone.utc)
    db.add(message)
    await db.commit()

    await _broadcast_discussion(
        archive_id, jsonable_encoder({"type": "delete", "message_id": message_id})
    )
    return {"success": True}


@router.patch("/{course_id}/archives/{archive_id}")
async def update_archive(
    course_id: int,
    archive_id: int,
    name: str = Form(None),
    professor: str = Form(None),
    archive_type: ArchiveType = Form(None),
    has_answers: bool = Form(None),
    academic_year: int = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update archive information. Only admins can update archives.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update archives",
        )

    query = select(Archive).where(
        Archive.course_id == course_id,
        Archive.id == archive_id,
        Archive.deleted_at.is_(None),
    )
    result = await db.execute(query)
    archive = result.scalar_one_or_none()

    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found"
        )

    if name is not None:
        archive.name = name
    if professor is not None:
        archive.professor = professor
    if archive_type is not None:
        archive.archive_type = archive_type
    if has_answers is not None:
        archive.has_answers = has_answers
    if academic_year is not None:
        archive.academic_year = academic_year

    archive.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(archive)

    return archive


@router.patch("/{course_id}/archives/{archive_id}/course")
async def update_archive_course(
    course_id: int,
    archive_id: int,
    course_update: ArchiveUpdateCourse,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update archive's course. Only admins can change archive's course.
    Supports both transferring to existing course by ID or creating new
    course by name and category.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change archive's course",
        )

    archive_query = select(Archive).where(
        Archive.course_id == course_id,
        Archive.id == archive_id,
        Archive.deleted_at.is_(None),
    )
    archive_result = await db.execute(archive_query)
    archive = archive_result.scalar_one_or_none()

    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found"
        )

    # Determine target course
    new_course = None

    if course_update.course_id:
        # Check if trying to transfer to the same course
        if course_update.course_id == course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer archive to the same course",
            )

        # Transfer to existing course by ID
        new_course_query = select(Course).where(
            Course.id == course_update.course_id, Course.deleted_at.is_(None)
        )
        new_course_result = await db.execute(new_course_query)
        new_course = new_course_result.scalar_one_or_none()

        if not new_course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Target course not found"
            )
    elif course_update.course_name and course_update.course_category:
        # Transfer to course by name and category, create if not exists
        new_course_query = select(Course).where(
            Course.name == course_update.course_name,
            Course.category == course_update.course_category,
            Course.deleted_at.is_(None),
        )
        new_course_result = await db.execute(new_course_query)
        new_course = new_course_result.scalar_one_or_none()

        if new_course:
            # Check if trying to transfer to the same course
            if new_course.id == course_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot transfer archive to the same course",
                )
        else:
            # Create new course if it doesn't exist
            new_course = Course(
                name=course_update.course_name, category=course_update.course_category
            )
            db.add(new_course)
            await db.commit()
            await db.refresh(new_course)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Either course_id or both course_name and course_category "
                "must be provided"
            ),
        )

    archive.course_id = new_course.id
    archive.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(archive)

    return {
        "message": f"Archive moved to course '{new_course.name}'",
        "archive_id": archive.id,
        "old_course_id": course_id,
        "new_course_id": new_course.id,
    }


@router.delete("/{course_id}/archives/{archive_id}")
async def delete_archive(
    course_id: int,
    archive_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Soft delete an archive. Users can only delete their own uploads.
    Admins can delete any archive.
    """
    query = select(Archive).where(
        Archive.course_id == course_id,
        Archive.id == archive_id,
        Archive.deleted_at.is_(None),
    )
    result = await db.execute(query)
    archive = result.scalar_one_or_none()

    if not archive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found"
        )

    if not current_user.is_admin and archive.uploader_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this archive",
        )

    archive.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    return {"message": "Archive deleted successfully"}


@router.post("/admin/courses", response_model=CourseRead)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Create a new course. Only admins can create courses.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create courses",
        )

    query = select(Course).where(
        Course.name == course_data.name,
        Course.category == course_data.category,
        Course.deleted_at.is_(None),
    )
    result = await db.execute(query)
    existing_course = result.scalar_one_or_none()

    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this name and category already exists",
        )

    order_index = course_data.order_index
    if order_index is None:
        order_index = await _next_order_index(db, course_data.category)

    course = Course(
        name=course_data.name,
        category=course_data.category,
        order_index=order_index,
    )

    db.add(course)
    await db.commit()
    await db.refresh(course)

    return course


@router.put("/admin/courses/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update a course. Only admins can update courses.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update courses",
        )

    query = select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))
    result = await db.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    original_category = course.category

    if course_data.name is not None or course_data.category is not None:
        new_name = course_data.name if course_data.name is not None else course.name
        new_category = (
            course_data.category
            if course_data.category is not None
            else course.category
        )

        if new_name != course.name or new_category != course.category:
            check_query = select(Course).where(
                Course.name == new_name,
                Course.category == new_category,
                Course.id != course_id,
                Course.deleted_at.is_(None),
            )
            check_result = await db.execute(check_query)
            existing_course = check_result.scalar_one_or_none()

            if existing_course:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course with this name and category already exists",
                )

    if course_data.name is not None:
        course.name = course_data.name
    if course_data.category is not None:
        course.category = course_data.category
        if course_data.category != original_category and course_data.order_index is None:
            course.order_index = await _next_order_index(db, course_data.category)
    if course_data.order_index is not None:
        course.order_index = course_data.order_index

    await db.commit()
    await db.refresh(course)

    return course


@router.post("/admin/courses/reorder", response_model=List[CourseRead])
async def reorder_courses(
    reorder_data: CourseReorder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update course order within one category. Only admins can reorder courses.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reorder courses",
        )

    result = await db.execute(
        select(Course).where(
            Course.category == reorder_data.category,
            Course.deleted_at.is_(None),
        )
    )
    courses = result.scalars().all()
    courses_by_id = {course.id: course for course in courses}

    requested_ids = list(dict.fromkeys(reorder_data.course_ids))
    missing_ids = [course_id for course_id in requested_ids if course_id not in courses_by_id]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course order includes courses outside the selected category",
        )

    ordered_courses = [courses_by_id[course_id] for course_id in requested_ids]
    ordered_id_set = set(requested_ids)
    remaining_courses = sorted(
        (course for course in courses if course.id not in ordered_id_set),
        key=_course_sort_key,
    )

    for index, course in enumerate([*ordered_courses, *remaining_courses]):
        course.order_index = index

    await db.commit()

    result = await db.execute(
        select(Course).where(
            Course.category == reorder_data.category,
            Course.deleted_at.is_(None),
        )
    )
    return _visible_courses(result.scalars().all())


@router.delete("/admin/courses/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Delete a course. Only admins can delete courses.
    This will also soft delete all associated archives.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete courses",
        )

    query = select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))
    result = await db.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    archives_query = select(Archive).where(
        Archive.course_id == course_id, Archive.deleted_at.is_(None)
    )
    archives_result = await db.execute(archives_query)
    archives = archives_result.scalars().all()

    # Soft delete all associated archives and the course
    current_time = datetime.now(timezone.utc)
    for archive in archives:
        archive.deleted_at = current_time

    # Soft delete the course
    course.deleted_at = current_time

    await db.commit()

    return {
        "message": (
            f"Course '{course.name}' and {len(archives)} associated "
            f"archives deleted successfully"
        )
    }


@router.get("/admin/courses", response_model=List[CourseRead])
async def list_all_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all courses with full details. Only admins can access this.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access all courses",
        )

    query = select(Course).where(Course.deleted_at.is_(None))
    result = await db.execute(query)
    courses = _visible_courses(result.scalars().all())

    return courses
