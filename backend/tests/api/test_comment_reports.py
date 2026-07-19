import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import delete, func
from sqlmodel import select

from app.main import app
from app.models.models import (
    Archive,
    ArchiveDiscussionMessage,
    ArchiveType,
    CommentReport,
    Course,
    CourseCategory,
    PersonalNotification,
    SystemIssueReport,
    UserRoles,
)
from app.utils.auth import get_current_user


def _override_user(user_id: int, *, is_admin: bool = False):
    async def _get_current_user():
        return UserRoles(user_id=user_id, is_admin=is_admin)

    return _get_current_user


async def _create_report_context(session_maker, author_id: int):
    unique = uuid.uuid4().hex[:8]
    async with session_maker() as session:
        course = Course(
            name=f"Report Course {unique}", category=CourseCategory.FRESHMAN
        )
        session.add(course)
        await session.commit()
        await session.refresh(course)
        archive = Archive(
            name=f"Report Exam {unique}",
            academic_year=2024,
            archive_type=ArchiveType.FINAL,
            professor="Prof",
            object_name=f"report-{unique}.pdf",
            uploader_id=author_id,
            course_id=course.id,
        )
        session.add(archive)
        await session.commit()
        await session.refresh(archive)
        messages = [
            ArchiveDiscussionMessage(
                archive_id=archive.id, user_id=author_id, content=f"report target {index}"
            )
            for index in range(3)
        ]
        session.add_all(messages)
        await session.commit()
        for message in messages:
            await session.refresh(message)
    return course, archive, messages


@pytest.mark.asyncio
async def test_comment_report_creation_validates_auth_reason_scope_and_duplicates(
    client, session_maker, make_user
):
    reporter = await make_user(name="comment-reporter")
    author = await make_user(name="comment-author", nickname="Reported Author")
    course, archive, messages = await _create_report_context(session_maker, author.id)
    path = f"/reports/courses/{course.id}/archives/{archive.id}/comments/{messages[0].id}"
    try:
        assert (
            await client.post(path, json={"report_reason": "misinformation"})
        ).status_code == 401

        app.dependency_overrides[get_current_user] = _override_user(reporter.id)
        blank_other = await client.post(
            path, json={"report_reason": "other", "custom_message": "   "}
        )
        assert blank_other.status_code == 422
        wrong_archive = await client.post(
            f"/reports/courses/{course.id}/archives/{archive.id + 999}/comments/{messages[0].id}",
            json={"report_reason": "misinformation"},
        )
        assert wrong_archive.status_code == 404

        created = await client.post(path, json={"report_reason": "misinformation"})
        assert created.status_code == 201
        body = created.json()
        assert body["comment_content_snapshot"] == messages[0].content
        assert body["comment_author_name"] == "Reported Author"
        assert body["source_exists"] is True
        assert (
            await client.post(path, json={"report_reason": "misinformation"})
        ).status_code == 409

        async with session_maker() as session:
            notification = await session.scalar(
                select(PersonalNotification).where(
                    PersonalNotification.user_id == reporter.id,
                    PersonalNotification.notification_type == "comment_report_submitted",
                    PersonalNotification.source_id == body["id"],
                )
            )
            assert notification is not None
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        async with session_maker() as session:
            await session.execute(
                delete(PersonalNotification).where(
                    PersonalNotification.user_id == reporter.id
                )
            )
            await session.execute(
                delete(CommentReport).where(CommentReport.archive_id == archive.id)
            )
            await session.execute(
                delete(ArchiveDiscussionMessage).where(
                    ArchiveDiscussionMessage.archive_id == archive.id
                )
            )
            await session.execute(delete(Archive).where(Archive.id == archive.id))
            await session.execute(delete(Course).where(Course.id == course.id))
            await session.commit()


@pytest.mark.asyncio
async def test_comment_report_admin_review_is_authorized_atomic_and_idempotent(
    client, session_maker, make_user
):
    reporter = await make_user(name="review-reporter")
    author = await make_user(name="review-author")
    admin = await make_user(name="review-admin", is_admin=True)
    course, archive, messages = await _create_report_context(session_maker, author.id)
    try:
        app.dependency_overrides[get_current_user] = _override_user(reporter.id)
        report_ids = []
        for message in messages:
            response = await client.post(
                f"/reports/courses/{course.id}/archives/{archive.id}/comments/{message.id}",
                json={"report_reason": "spam_or_duplicate"},
            )
            assert response.status_code == 201
            report_ids.append(response.json()["id"])
        assert (await client.get("/reports/admin/comments")).status_code == 403
        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "dismissed", "admin_response": "forbidden"},
            )
        ).status_code == 403

        async with session_maker() as session:
            missing_source = await session.get(ArchiveDiscussionMessage, messages[1].id)
            missing_source.deleted_at = datetime.now(timezone.utc)
            session.add(missing_source)
            await session.commit()

        app.dependency_overrides[get_current_user] = _override_user(admin.id, is_admin=True)
        in_review = await client.patch(
            f"/reports/admin/comments/{report_ids[0]}",
            json={"status": "in_review", "admin_response": "正在確認"},
        )
        assert in_review.status_code == 200
        finalized = await client.patch(
            f"/reports/admin/comments/{report_ids[0]}",
            json={"status": "upheld", "admin_response": "已完成審核"},
        )
        assert finalized.status_code == 200
        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "upheld", "admin_response": "重送"},
            )
        ).status_code == 200

        missing_result = await client.patch(
            f"/reports/admin/comments/{report_ids[1]}",
            json={"status": "dismissed", "admin_response": "來源已不存在，仍完成審核"},
        )
        assert missing_result.status_code == 200
        assert missing_result.json()["source_exists"] is False

        deleted_result = await client.patch(
            f"/reports/admin/comments/{report_ids[2]}",
            json={
                "status": "upheld",
                "admin_response": "回報成立並刪除留言",
                "delete_comment": True,
            },
        )
        assert deleted_result.status_code == 200
        assert deleted_result.json()["comment_deleted"] is True

        async with session_maker() as session:
            result_count = int(
                await session.scalar(
                    select(func.count(PersonalNotification.id)).where(
                        PersonalNotification.user_id == reporter.id,
                        PersonalNotification.notification_type == "comment_report_result",
                    )
                )
                or 0
            )
            assert result_count == 3
            deleted_message = await session.get(ArchiveDiscussionMessage, messages[2].id)
            assert deleted_message.deleted_at is not None
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        async with session_maker() as session:
            await session.execute(
                delete(PersonalNotification).where(
                    PersonalNotification.user_id == reporter.id
                )
            )
            await session.execute(
                delete(CommentReport).where(CommentReport.archive_id == archive.id)
            )
            await session.execute(
                delete(ArchiveDiscussionMessage).where(
                    ArchiveDiscussionMessage.archive_id == archive.id
                )
            )
            await session.execute(delete(Archive).where(Archive.id == archive.id))
            await session.execute(delete(Course).where(Course.id == course.id))
            await session.commit()


@pytest.mark.asyncio
async def test_system_issue_reports_are_local_admin_only_and_filter_unsafe_github_urls(
    client, session_maker, make_user
):
    reporter = await make_user(name="system-issue-reporter")
    admin = await make_user(name="system-issue-admin", is_admin=True)
    payload = {
        "report_type": "bug",
        "title": "System issue",
        "description": "Steps to reproduce",
        "contact": "reporter@example.com",
        "metadata": {"route": {"path": "/archive"}},
    }
    assert (await client.post("/reports/system-issues", json=payload)).status_code == 401
    try:
        app.dependency_overrides[get_current_user] = _override_user(reporter.id)
        created = await client.post("/reports/system-issues", json=payload)
        assert created.status_code == 201
        body = created.json()
        assert body["github_issue_number"] is None
        assert body["github_issue_url"] is None
        assert body["status"] == "local_only"
        assert (await client.get("/reports/admin/system-issues")).status_code == 403

        async with session_maker() as session:
            report = await session.get(SystemIssueReport, body["id"])
            report.github_issue_number = 123
            report.github_issue_url = "https://evil.example/issues/123"
            session.add(report)
            await session.commit()

        app.dependency_overrides[get_current_user] = _override_user(admin.id, is_admin=True)
        listed = await client.get("/reports/admin/system-issues")
        assert listed.status_code == 200
        item = next(item for item in listed.json()["items"] if item["id"] == body["id"])
        assert item["github_issue_number"] == 123
        assert item["github_issue_url"] is None
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        async with session_maker() as session:
            await session.execute(
                delete(SystemIssueReport).where(
                    SystemIssueReport.reporter_user_id == reporter.id
                )
            )
            await session.commit()
