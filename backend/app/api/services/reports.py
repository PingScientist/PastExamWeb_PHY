import json
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.models.models import (
    Archive,
    ArchiveDiscussionMessage,
    CommentReport,
    CommentReportAdminUpdate,
    CommentReportCreate,
    CommentReportListRead,
    CommentReportRead,
    CommentReportReason,
    CommentReportStatus,
    Course,
    PersonalNotificationType,
    SystemIssueReport,
    SystemIssueReportCreate,
    SystemIssueReportListRead,
    SystemIssueReportRead,
    User,
    UserRoles,
)
from app.services.discussions import soft_delete_discussion_message
from app.services.personal_notifications import enqueue_personal_notification
from app.utils.auth import get_current_user

router = APIRouter()

FINAL_REPORT_STATUSES = {
    CommentReportStatus.UPHELD.value,
    CommentReportStatus.DISMISSED.value,
}
REPORT_REASON_LABELS = {
    CommentReportReason.SPAM_OR_DUPLICATE.value: "垃圾訊息或重複洗版",
    CommentReportReason.HARASSMENT_OR_HOSTILITY.value: "攻擊、騷擾或不友善內容",
    CommentReportReason.INAPPROPRIATE_OR_ILLEGAL.value: "不當或違法內容",
    CommentReportReason.PRIVACY_VIOLATION.value: "洩漏個人資料或隱私",
    CommentReportReason.MISINFORMATION.value: "錯誤或誤導資訊",
    CommentReportReason.OTHER.value: "其他",
}
SYSTEM_ISSUE_TYPES = {"bug", "enhancement", "performance", "ui-ux", "question"}
GITHUB_ISSUE_URL_PATTERN = re.compile(
    r"^https://github\.com/PingScientist/PastExamWeb_PHY/issues/(?P<number>[1-9][0-9]*)$"
)


def _display_name(user_id: int | None, nickname: str | None, name: str | None) -> str:
    if user_id is None:
        return "已刪除使用者"
    return (nickname or name or f"使用者 {user_id}").strip()


def _require_admin(current_user: UserRoles) -> None:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )


def _report_select():
    reporter = aliased(User)
    author = aliased(User)
    reviewer = aliased(User)
    source = aliased(ArchiveDiscussionMessage)
    statement = (
        select(
            CommentReport,
            reporter.nickname,
            reporter.name,
            author.nickname,
            author.name,
            reviewer.nickname,
            reviewer.name,
            source.id,
        )
        .outerjoin(reporter, reporter.id == CommentReport.reporter_user_id)
        .outerjoin(author, author.id == CommentReport.comment_author_id)
        .outerjoin(reviewer, reviewer.id == CommentReport.reviewed_by)
        .outerjoin(
            source,
            (source.id == CommentReport.comment_id) & (source.deleted_at.is_(None)),
        )
    )
    return statement, reporter, author, reviewer


def _serialize_report(row) -> CommentReportRead:
    report = row[0]
    return CommentReportRead(
        id=report.id,
        reporter_user_id=report.reporter_user_id,
        reporter_name=_display_name(report.reporter_user_id, row[1], row[2]),
        comment_id=report.comment_id,
        comment_author_id=report.comment_author_id,
        comment_author_name=(
            _display_name(report.comment_author_id, row[3], row[4])
            if report.comment_author_id and (row[3] or row[4])
            else report.comment_author_name_snapshot
        ),
        archive_id=report.archive_id,
        course_id=report.course_id,
        thread_id=report.thread_id,
        reply_to_message_id=report.reply_to_message_id,
        reason=report.reason,
        custom_message=report.custom_message,
        comment_content_snapshot=report.comment_content_snapshot,
        comment_created_at_snapshot=report.comment_created_at_snapshot,
        archive_name=report.archive_name_snapshot,
        course_name=report.course_name_snapshot,
        status=report.status,
        admin_response=report.admin_response,
        reviewed_by=report.reviewed_by,
        reviewer_name=(
            _display_name(report.reviewed_by, row[5], row[6])
            if report.reviewed_by
            else None
        ),
        reviewed_at=report.reviewed_at,
        comment_deleted=report.comment_deleted,
        source_exists=row[7] is not None,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


async def _read_report(db: AsyncSession, report_id: int) -> CommentReportRead:
    statement, _, _, _ = _report_select()
    row = (await db.execute(statement.where(CommentReport.id == report_id))).one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment report not found"
        )
    return _serialize_report(row)


def _safe_github_issue_url(report: SystemIssueReport) -> str | None:
    if not report.github_issue_url or report.github_issue_number is None:
        return None
    match = GITHUB_ISSUE_URL_PATTERN.fullmatch(report.github_issue_url)
    if not match or int(match.group("number")) != report.github_issue_number:
        return None
    return report.github_issue_url


def _serialize_system_issue(report: SystemIssueReport, nickname, name) -> SystemIssueReportRead:
    return SystemIssueReportRead(
        id=report.id,
        reporter_user_id=report.reporter_user_id,
        reporter_name=_display_name(report.reporter_user_id, nickname, name),
        report_type=report.report_type,
        title=report.title,
        description=report.description,
        contact=report.contact,
        status=report.status,
        github_issue_number=report.github_issue_number,
        github_issue_url=_safe_github_issue_url(report),
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.post(
    "/system-issues",
    response_model=SystemIssueReportRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_system_issue_report(
    payload: SystemIssueReportCreate,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    report_type = payload.report_type.strip()
    title = payload.title.strip()
    description = payload.description.strip()
    if report_type not in SYSTEM_ISSUE_TYPES or not title or not description:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid system issue report",
        )
    metadata = payload.metadata or {}
    if len(json.dumps(metadata, ensure_ascii=False, default=str)) > 10_000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="System issue metadata is too large",
        )
    report = SystemIssueReport(
        reporter_user_id=current_user.user_id,
        report_type=report_type,
        title=title,
        description=description,
        contact=(payload.contact or "").strip() or None,
        metadata_json=metadata,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    user = await db.get(User, current_user.user_id)
    return _serialize_system_issue(
        report,
        user.nickname if user else None,
        user.name if user else None,
    )


@router.get("/admin/system-issues", response_model=SystemIssueReportListRead)
async def list_system_issue_reports(
    search: str | None = Query(default=None, max_length=100),
    report_type: str | None = Query(default=None, max_length=40),
    report_status: str | None = Query(default=None, alias="status", max_length=30),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    reporter = aliased(User)
    statement = select(SystemIssueReport, reporter.nickname, reporter.name).outerjoin(
        reporter, reporter.id == SystemIssueReport.reporter_user_id
    )
    filters = []
    normalized_search = (search or "").strip()
    if normalized_search:
        pattern = f"%{normalized_search}%"
        filters.append(
            or_(
                SystemIssueReport.title.ilike(pattern),
                SystemIssueReport.description.ilike(pattern),
                reporter.name.ilike(pattern),
                reporter.nickname.ilike(pattern),
            )
        )
    if report_type:
        if report_type not in SYSTEM_ISSUE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid system issue report type",
            )
        filters.append(SystemIssueReport.report_type == report_type)
    if report_status:
        filters.append(SystemIssueReport.status == report_status)
    if filters:
        statement = statement.where(*filters)

    sort_fields = {
        "created_at": SystemIssueReport.created_at,
        "reporter": func.coalesce(reporter.nickname, reporter.name, ""),
        "title": SystemIssueReport.title,
        "report_type": SystemIssueReport.report_type,
        "status": SystemIssueReport.status,
    }
    sort_column = sort_fields.get(sort_by)
    if sort_column is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid system issue sort field",
        )
    total = int(
        await db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    )
    ordering = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    rows = (
        await db.execute(
            statement.order_by(ordering, SystemIssueReport.id.desc())
            .offset(offset)
            .limit(limit)
        )
    ).all()
    return SystemIssueReportListRead(
        items=[_serialize_system_issue(row[0], row[1], row[2]) for row in rows],
        total=total,
    )


@router.post(
    "/courses/{course_id}/archives/{archive_id}/comments/{comment_id}",
    response_model=CommentReportRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment_report(
    course_id: int,
    archive_id: int,
    comment_id: int,
    payload: CommentReportCreate,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    custom_message = (payload.custom_message or "").strip()
    if payload.report_reason == CommentReportReason.OTHER and not custom_message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Custom message is required for the other reason",
        )

    row = (
        await db.execute(
            select(ArchiveDiscussionMessage, Archive, Course, User)
            .join(Archive, Archive.id == ArchiveDiscussionMessage.archive_id)
            .join(Course, Course.id == Archive.course_id)
            .join(User, User.id == ArchiveDiscussionMessage.user_id)
            .where(
                ArchiveDiscussionMessage.id == comment_id,
                ArchiveDiscussionMessage.archive_id == archive_id,
                ArchiveDiscussionMessage.deleted_at.is_(None),
                Archive.id == archive_id,
                Archive.course_id == course_id,
                Archive.deleted_at.is_(None),
                Course.id == course_id,
                Course.deleted_at.is_(None),
            )
        )
    ).one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    message, archive, course, author = row
    reason = payload.report_reason.value
    duplicate = await db.scalar(
        select(CommentReport.id).where(
            CommentReport.reporter_user_id == current_user.user_id,
            CommentReport.comment_id == comment_id,
            CommentReport.reason == reason,
            CommentReport.status.in_(
                [CommentReportStatus.PENDING.value, CommentReportStatus.IN_REVIEW.value]
            ),
        )
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active report for this comment and reason",
        )

    report = CommentReport(
        reporter_user_id=current_user.user_id,
        comment_id=message.id,
        comment_author_id=message.user_id,
        archive_id=archive.id,
        course_id=course.id,
        thread_id=message.parent_id or message.id,
        reply_to_message_id=message.reply_to_message_id,
        reason=reason,
        custom_message=custom_message if payload.report_reason == CommentReportReason.OTHER else None,
        comment_content_snapshot=message.content,
        comment_author_name_snapshot=_display_name(author.id, author.nickname, author.name),
        comment_created_at_snapshot=message.created_at,
        archive_name_snapshot=archive.name,
        course_name_snapshot=course.name,
    )
    db.add(report)
    try:
        await db.flush()
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active report for this comment and reason",
        ) from error

    await enqueue_personal_notification(
        db,
        user_id=current_user.user_id,
        notification_type=PersonalNotificationType.COMMENT_REPORT_SUBMITTED,
        title="留言回報已成功送出",
        message=f"原因：{REPORT_REASON_LABELS[reason]}。請等待管理員審核。",
        source_type="comment_report",
        source_id=report.id,
        metadata={"report_id": report.id, "reason": reason, "status": report.status},
        dedupe_key=f"comment_report_submitted:{report.id}",
    )
    await db.commit()
    return await _read_report(db, report.id)


@router.get("/admin/comments", response_model=CommentReportListRead)
async def list_comment_reports(
    report_status: CommentReportStatus | None = Query(default=None, alias="status"),
    reason: CommentReportReason | None = None,
    search: str | None = Query(default=None, max_length=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    statement, reporter, author, reviewer = _report_select()
    filters = []
    if report_status:
        filters.append(CommentReport.status == report_status.value)
    if reason:
        filters.append(CommentReport.reason == reason.value)
    normalized_search = (search or "").strip()
    if normalized_search:
        pattern = f"%{normalized_search}%"
        filters.append(
            or_(
                CommentReport.comment_content_snapshot.ilike(pattern),
                CommentReport.course_name_snapshot.ilike(pattern),
                CommentReport.archive_name_snapshot.ilike(pattern),
                reporter.name.ilike(pattern),
                reporter.nickname.ilike(pattern),
                author.name.ilike(pattern),
                author.nickname.ilike(pattern),
            )
        )
    if filters:
        statement = statement.where(*filters)
    total = int(
        await db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    )
    sort_fields = {
        "created_at": CommentReport.created_at,
        "status": CommentReport.status,
        "reason": CommentReport.reason,
        "reporter": func.coalesce(reporter.nickname, reporter.name, ""),
        "comment_author": func.coalesce(author.nickname, author.name, ""),
        "course_archive": func.coalesce(CommentReport.course_name_snapshot, ""),
        "reviewer": func.coalesce(reviewer.nickname, reviewer.name, ""),
        "reviewed_at": CommentReport.reviewed_at,
    }
    sort_column = sort_fields.get(sort_by)
    if sort_column is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid comment report sort field",
        )
    ordering = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    rows = (
        await db.execute(
            statement.order_by(ordering, CommentReport.id.desc())
            .offset(offset)
            .limit(limit)
        )
    ).all()
    return CommentReportListRead(
        items=[_serialize_report(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/admin/comments/{report_id}", response_model=CommentReportRead)
async def get_comment_report(
    report_id: int,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    return await _read_report(db, report_id)


@router.patch("/admin/comments/{report_id}", response_model=CommentReportRead)
async def review_comment_report(
    report_id: int,
    payload: CommentReportAdminUpdate,
    current_user: UserRoles = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    _require_admin(current_user)
    report = (
        await db.execute(
            select(CommentReport)
            .where(CommentReport.id == report_id)
            .with_for_update()
        )
    ).scalar_one_or_none()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment report not found"
        )

    new_status = payload.status.value
    if report.status in FINAL_REPORT_STATUSES:
        if report.status == new_status:
            return await _read_report(db, report.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A finalized report cannot be changed",
        )
    if new_status == CommentReportStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A report cannot return to pending",
        )

    response = (payload.admin_response or "").strip()
    is_final = new_status in FINAL_REPORT_STATUSES
    if is_final and not response:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Admin response is required for a final result",
        )
    if payload.delete_comment and new_status != CommentReportStatus.UPHELD.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only an upheld report can delete the source comment",
        )

    now = datetime.now(timezone.utc)
    report.status = new_status
    report.admin_response = response or None
    report.reviewed_by = current_user.user_id
    report.reviewed_at = now
    report.updated_at = now
    if payload.delete_comment and report.comment_id is not None:
        source = (
            await db.execute(
                select(ArchiveDiscussionMessage).where(
                    ArchiveDiscussionMessage.id == report.comment_id,
                    ArchiveDiscussionMessage.archive_id == report.archive_id,
                    ArchiveDiscussionMessage.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if source is not None:
            await soft_delete_discussion_message(db, source)
            report.comment_deleted = True

    db.add(report)
    if is_final:
        result_label = "回報成立／已處理" if new_status == CommentReportStatus.UPHELD.value else "回報不成立"
        await enqueue_personal_notification(
            db,
            user_id=report.reporter_user_id,
            notification_type=PersonalNotificationType.COMMENT_REPORT_RESULT,
            title="留言回報審核完成",
            message=(
                f"審核結果：{result_label}。管理員答覆：{response}。"
                f"處置：{'留言已刪除' if report.comment_deleted else '未刪除留言'}。"
            ),
            source_type="comment_report",
            source_id=report.id,
            metadata={
                "report_id": report.id,
                "status": new_status,
                "comment_deleted": report.comment_deleted,
                "reviewed_at": now.isoformat(),
            },
            dedupe_key=f"comment_report_result:{report.id}:{new_status}",
        )
    await db.commit()
    return await _read_report(db, report.id)
