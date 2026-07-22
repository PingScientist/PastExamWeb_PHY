import asyncio
import uuid
from datetime import datetime, timezone

import httpx
import pytest
from sqlalchemy import delete, func
from sqlmodel import select

from app.api.services import reports as reports_service
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
from app.services.github_issues import GitHubIssuesClient
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
            assert notification.title == "留言回報已成功送出"
            assert "回報編號" not in notification.message
            assert f"#{body['id']}" not in notification.message
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
    client, session_maker, make_user, monkeypatch
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
        sorted_page = await client.get(
            "/reports/admin/comments",
            params={"sort_by": "reason", "sort_order": "asc", "limit": 1, "offset": 1},
        )
        assert sorted_page.status_code == 200
        assert sorted_page.json()["total"] == 3
        assert len(sorted_page.json()["items"]) == 1
        assert (
            await client.get(
                "/reports/admin/comments", params={"sort_by": "comment_snapshot"}
            )
        ).status_code == 422

        assert (
            await client.get(
                "/reports/admin/comments", params={"status": "in_review"}
            )
        ).status_code == 422
        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "in_review", "admin_response": "正在確認"},
            )
        ).status_code == 422

        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "pending", "admin_response": "   "},
            )
        ).status_code == 422

        original_enqueue = reports_service.enqueue_personal_notification

        async def fail_notification(*args, **kwargs):
            raise RuntimeError("notification insert failed")

        monkeypatch.setattr(
            reports_service, "enqueue_personal_notification", fail_notification
        )
        with pytest.raises(RuntimeError, match="notification insert failed"):
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "upheld", "admin_response": None},
            )
        monkeypatch.setattr(
            reports_service, "enqueue_personal_notification", original_enqueue
        )
        async with session_maker() as session:
            rolled_back_report = await session.get(CommentReport, report_ids[0])
            assert rolled_back_report.status == "pending"
            assert int(
                await session.scalar(
                    select(func.count(PersonalNotification.id)).where(
                        PersonalNotification.user_id == reporter.id,
                        PersonalNotification.notification_type
                        == "comment_report_result",
                    )
                )
                or 0
            ) == 0

        finalized = await client.patch(
            f"/reports/admin/comments/{report_ids[0]}",
            json={"status": "upheld", "admin_response": "   "},
        )
        assert finalized.status_code == 200
        assert finalized.json()["admin_response"] is None
        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "upheld", "admin_response": "修改答覆"},
            )
        ).status_code == 409
        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "dismissed", "admin_response": None},
            )
        ).status_code == 409
        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={
                    "status": "upheld",
                    "admin_response": None,
                    "delete_comment": True,
                },
            )
        ).status_code == 409
        assert (
            await client.patch(
                f"/reports/admin/comments/{report_ids[0]}",
                json={"status": "pending", "admin_response": None},
            )
        ).status_code == 409

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
            locked_report = await session.get(CommentReport, report_ids[0])
            assert locked_report.status == "upheld"
            assert locked_report.admin_response is None
            assert locked_report.comment_deleted is False
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
            result_notifications = list(
                (
                    await session.execute(
                        select(PersonalNotification).where(
                            PersonalNotification.user_id == reporter.id,
                            PersonalNotification.notification_type
                            == "comment_report_result",
                            PersonalNotification.source_id == report_ids[0],
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(result_notifications) == 1
            assert result_notifications[0].dedupe_key == (
                f"comment_report_result:{report_ids[0]}"
            )
            assert any(
                "管理員答覆：未提供答覆" in item.message
                for item in result_notifications
            )
            result_notification = await session.scalar(
                select(PersonalNotification).where(
                    PersonalNotification.user_id == reporter.id,
                    PersonalNotification.notification_type == "comment_report_result",
                    PersonalNotification.source_id == report_ids[0],
                )
            )
            assert result_notification.title == "留言回報審核完成"
            assert "回報編號" not in result_notification.title
            assert "回報編號" not in result_notification.message
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

        app.dependency_overrides[get_current_user] = _override_user(
            admin.id, is_admin=True
        )
        listed = await client.get(
            "/reports/admin/system-issues",
            params={"search": "System issue", "sort_by": "title", "sort_order": "asc"},
        )
        assert listed.status_code == 200
        item = next(item for item in listed.json()["items"] if item["id"] == body["id"])
        assert item["github_issue_number"] == 123
        assert item["github_issue_url"] is None
        assert (
            await client.get(
                "/reports/admin/system-issues", params={"sort_by": "description"}
            )
        ).status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        async with session_maker() as session:
            await session.execute(
                delete(SystemIssueReport).where(
                    SystemIssueReport.reporter_user_id == reporter.id
                )
            )
            await session.commit()


@pytest.mark.asyncio
async def test_system_issue_reports_link_github_with_retry_and_idempotency(
    client, session_maker, make_user, monkeypatch
):
    reporter = await make_user(name="github-report-reporter")
    admin = await make_user(name="github-report-admin", is_admin=True)
    created_report_ids = []
    github_requests = []

    def success_handler(request: httpx.Request) -> httpx.Response:
        github_requests.append(request)
        report_marker = len(github_requests)
        return httpx.Response(
            201,
            json={
                "number": 500 + report_marker,
                "html_url": (
                    "https://github.com/PingScientist/PastExamWeb_PHY/issues/"
                    f"{500 + report_marker}"
                ),
                "state": "open",
            },
        )

    success_client = GitHubIssuesClient(
        enabled=True,
        token="mock-token",
        transport=httpx.MockTransport(success_handler),
    )
    try:
        monkeypatch.setattr(
            reports_service,
            "get_github_issues_client",
            lambda: success_client,
        )
        app.dependency_overrides[get_current_user] = _override_user(reporter.id)
        linked = await client.post(
            "/reports/system-issues",
            json={
                "report_type": "bug",
                "title": "GitHub linked report",
                "description": "Create through mocked GitHub HTTP",
                "contact": "private@example.com",
                "metadata": {"route": {"path": "/archive"}},
            },
        )
        assert linked.status_code == 201
        linked_body = linked.json()
        created_report_ids.append(linked_body["id"])
        assert linked_body["github_linked"] is True
        assert linked_body["github_issue_number"] == 501
        assert linked_body["github_issue_state"] == "open"

        app.dependency_overrides[get_current_user] = _override_user(
            admin.id, is_admin=True
        )
        repeated = await client.post(
            f"/reports/admin/system-issues/{linked_body['id']}/github-issue"
        )
        assert repeated.status_code == 200
        assert repeated.json()["github_issue_number"] == 501
        assert len(github_requests) == 1

        def failure_handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, json={"message": "mock-token internal detail"})

        failure_client = GitHubIssuesClient(
            enabled=True,
            token="mock-token",
            transport=httpx.MockTransport(failure_handler),
        )
        monkeypatch.setattr(
            reports_service,
            "get_github_issues_client",
            lambda: failure_client,
        )
        app.dependency_overrides[get_current_user] = _override_user(reporter.id)
        failed_link = await client.post(
            "/reports/system-issues",
            json={
                "report_type": "performance",
                "title": "GitHub retry report",
                "description": "Keep the local report when GitHub fails",
            },
        )
        assert failed_link.status_code == 201
        failed_body = failed_link.json()
        created_report_ids.append(failed_body["id"])
        assert failed_body["github_linked"] is False
        assert failed_body["github_issue_number"] is None
        assert failed_body["github_issue_url"] is None
        assert failed_body["github_sync_status"] == "failed"
        assert "mock-token" not in failed_body["github_sync_error"]

        app.dependency_overrides[get_current_user] = _override_user(
            admin.id, is_admin=True
        )
        failed_retry = await client.post(
            f"/reports/admin/system-issues/{failed_body['id']}/github-issue"
        )
        assert failed_retry.status_code == 502
        assert "mock-token" not in str(failed_retry.json())

        monkeypatch.setattr(
            reports_service,
            "get_github_issues_client",
            lambda: success_client,
        )
        app.dependency_overrides[get_current_user] = _override_user(
            reporter.id, is_admin=False
        )
        assert (
            await client.post(
                f"/reports/admin/system-issues/{failed_body['id']}/github-issue"
            )
        ).status_code == 403

        app.dependency_overrides[get_current_user] = _override_user(
            admin.id, is_admin=True
        )
        retried, duplicate_retry = await asyncio.gather(
            client.post(
                f"/reports/admin/system-issues/{failed_body['id']}/github-issue"
            ),
            client.post(
                f"/reports/admin/system-issues/{failed_body['id']}/github-issue"
            ),
        )
        assert retried.status_code == 200
        assert duplicate_retry.status_code == 200
        assert retried.json()["github_issue_number"] == 502
        assert duplicate_retry.json()["github_issue_number"] == 502
        assert len(github_requests) == 2
        assert (
            await client.post(
                f"/reports/admin/system-issues/{failed_body['id']}/github-issue"
            )
        ).status_code == 200
        assert len(github_requests) == 2

        disabled_client = GitHubIssuesClient(enabled=False, token="")
        monkeypatch.setattr(
            reports_service,
            "get_github_issues_client",
            lambda: disabled_client,
        )
        app.dependency_overrides[get_current_user] = _override_user(reporter.id)
        disabled = await client.post(
            "/reports/system-issues",
            json={
                "report_type": "question",
                "title": "No GitHub credential",
                "description": "The local report must still exist",
            },
        )
        assert disabled.status_code == 201
        disabled_body = disabled.json()
        created_report_ids.append(disabled_body["id"])
        assert disabled_body["github_linked"] is False
        assert disabled_body["github_sync_status"] == "disabled"
        assert disabled_body["github_issue_url"] is None

        async with session_maker() as session:
            for report_id in created_report_ids:
                assert await session.get(SystemIssueReport, report_id) is not None
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        async with session_maker() as session:
            await session.execute(
                delete(SystemIssueReport).where(
                    SystemIssueReport.id.in_(created_report_ids or [-1])
                )
            )
            await session.commit()


@pytest.mark.asyncio
async def test_admin_moves_report_records_to_independent_trash_and_restores_them(
    client, session_maker, make_user
):
    reporter = await make_user(name="trash-report-reporter")
    author = await make_user(name="trash-report-author")
    admin = await make_user(name="trash-report-admin", is_admin=True)
    course, archive, messages = await _create_report_context(session_maker, author.id)
    system_payload = {
        "report_type": "bug",
        "title": "Trashable system issue",
        "description": "Local report only",
        "metadata": {},
    }
    try:
        app.dependency_overrides[get_current_user] = _override_user(reporter.id)
        system_response = await client.post("/reports/system-issues", json=system_payload)
        comment_response = await client.post(
            f"/reports/courses/{course.id}/archives/{archive.id}/comments/{messages[0].id}",
            json={"report_reason": "misinformation"},
        )
        assert system_response.status_code == 201
        assert comment_response.status_code == 201
        system_id = system_response.json()["id"]
        comment_id = comment_response.json()["id"]

        assert (
            await client.delete(f"/reports/admin/system-issues/{system_id}")
        ).status_code == 403
        assert (
            await client.delete(f"/reports/admin/comments/{comment_id}")
        ).status_code == 403

        async with session_maker() as session:
            system_report = await session.get(SystemIssueReport, system_id)
            system_report.github_issue_number = 321
            system_report.github_issue_url = (
                "https://github.com/PingScientist/PastExamWeb_PHY/issues/321"
            )
            session.add(system_report)
            await session.commit()

        app.dependency_overrides[get_current_user] = _override_user(admin.id, is_admin=True)
        reviewed = await client.patch(
            f"/reports/admin/comments/{comment_id}",
            json={"status": "dismissed", "admin_response": "不成立"},
        )
        assert reviewed.status_code == 200

        async with session_maker() as session:
            notification_count_before = int(
                await session.scalar(
                    select(func.count(PersonalNotification.id)).where(
                        PersonalNotification.user_id == reporter.id
                    )
                )
                or 0
            )

        assert (
            await client.delete(f"/reports/admin/system-issues/{system_id}")
        ).status_code == 200
        assert (
            await client.delete(f"/reports/admin/comments/{comment_id}")
        ).status_code == 200
        assert (
            await client.post(
                f"/reports/admin/system-issues/{system_id}/github-issue"
            )
        ).status_code == 404

        system_list = await client.get("/reports/admin/system-issues")
        comment_list = await client.get("/reports/admin/comments")
        assert all(item["id"] != system_id for item in system_list.json()["items"])
        assert all(item["id"] != comment_id for item in comment_list.json()["items"])

        system_trash = await client.get(
            "/trash", params={"item_type": "system_issue_report"}
        )
        comment_trash = await client.get(
            "/trash", params={"item_type": "comment_report"}
        )
        archive_report_trash = await client.get(
            "/trash", params={"item_type": "archive_report"}
        )
        assert system_trash.status_code == 200
        assert comment_trash.status_code == 200
        assert archive_report_trash.json() == []
        trashed_system = next(item for item in system_trash.json() if item["id"] == system_id)
        trashed_comment = next(item for item in comment_trash.json() if item["id"] == comment_id)
        assert trashed_system["deleted_by_id"] == admin.id
        assert trashed_system["github_issue_number"] == 321
        assert trashed_system["dependencies"] == []
        assert trashed_comment["deleted_by_id"] == admin.id
        assert trashed_comment["comment_snapshot"] == messages[0].content
        assert trashed_comment["dependencies"] == []

        async with session_maker() as session:
            source = await session.get(ArchiveDiscussionMessage, messages[0].id)
            system_report = await session.get(SystemIssueReport, system_id)
            comment_report = await session.get(CommentReport, comment_id)
            notification_count_after_delete = int(
                await session.scalar(
                    select(func.count(PersonalNotification.id)).where(
                        PersonalNotification.user_id == reporter.id
                    )
                )
                or 0
            )
            assert source is not None and source.deleted_at is None
            assert system_report.github_issue_number == 321
            assert comment_report.status == "dismissed"
            assert notification_count_after_delete == notification_count_before

        assert (
            await client.post(
                "/trash/restore",
                json={"item_type": "system_issue_report", "item_id": system_id},
            )
        ).status_code == 200
        assert (
            await client.post(
                "/trash/restore",
                json={"item_type": "comment_report", "item_id": comment_id},
            )
        ).status_code == 200

        async with session_maker() as session:
            system_report = await session.get(SystemIssueReport, system_id)
            comment_report = await session.get(CommentReport, comment_id)
            notification_count_after_restore = int(
                await session.scalar(
                    select(func.count(PersonalNotification.id)).where(
                        PersonalNotification.user_id == reporter.id
                    )
                )
                or 0
            )
            assert system_report.deleted_at is None
            assert system_report.deleted_by_id is None
            assert system_report.github_issue_number == 321
            assert comment_report.deleted_at is None
            assert comment_report.deleted_by_id is None
            assert comment_report.status == "dismissed"
            assert comment_report.reviewed_by == admin.id
            assert comment_report.admin_response == "不成立"
            assert notification_count_after_restore == notification_count_before

        assert (
            await client.delete(f"/reports/admin/system-issues/{system_id}")
        ).status_code == 200
        assert (
            await client.delete(f"/reports/admin/comments/{comment_id}")
        ).status_code == 200
        assert (
            await client.delete(f"/trash/system_issue_report/{system_id}")
        ).status_code == 200
        assert (
            await client.delete(f"/trash/comment_report/{comment_id}")
        ).status_code == 200

        async with session_maker() as session:
            assert await session.get(SystemIssueReport, system_id) is None
            assert await session.get(CommentReport, comment_id) is None
            source = await session.get(ArchiveDiscussionMessage, messages[0].id)
            assert source is not None and source.deleted_at is None
            assert int(
                await session.scalar(
                    select(func.count(PersonalNotification.id)).where(
                        PersonalNotification.user_id == reporter.id
                    )
                )
                or 0
            ) == notification_count_before

        assert not any(
            item["id"] == system_id
            for item in (
                await client.get(
                    "/trash", params={"item_type": "system_issue_report"}
                )
            ).json()
        )
        assert not any(
            item["id"] == comment_id
            for item in (
                await client.get("/trash", params={"item_type": "comment_report"})
            ).json()
        )

        app.dependency_overrides[get_current_user] = _override_user(
            reporter.id, is_admin=False
        )
        center = (await client.get("/notifications/center")).json()
        result_notification = next(
            item
            for item in center["personal_notifications"]
            if item["source_type"] == "comment_report"
            and item["source_id"] == comment_id
        )
        assert result_notification["source_available"] is False
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
                delete(SystemIssueReport).where(
                    SystemIssueReport.reporter_user_id == reporter.id
                )
            )
            await session.execute(
                delete(ArchiveDiscussionMessage).where(
                    ArchiveDiscussionMessage.archive_id == archive.id
                )
            )
            await session.execute(delete(Archive).where(Archive.id == archive.id))
            await session.execute(delete(Course).where(Course.id == course.id))
            await session.commit()
