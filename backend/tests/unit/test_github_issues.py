import json

import httpx
import pytest

from app.models.models import SystemIssueReport
from app.services.github_issues import (
    GitHubIssueError,
    GitHubIssuesClient,
    build_issue_body,
    is_allowed_github_issue_url,
)


def _report() -> SystemIssueReport:
    return SystemIssueReport(
        id=42,
        reporter_user_id=7,
        report_type="bug",
        title="預覽失敗",
        description="點擊預覽後沒有反應",
        contact="private@example.com",
        metadata_json={
            "userAgent": "Browser 1.0",
            "platform": "Test OS",
            "language": "zh-TW",
            "route": {"path": "/archive", "fullPath": "/archive?secret=value"},
            "pageContext": {"searchQuery": "private query"},
            "timestamp": "2026-07-22T13:00:00Z",
        },
    )


@pytest.mark.asyncio
async def test_github_client_creates_issue_with_safe_headers_and_internal_marker():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(
            201,
            json={
                "number": 123,
                "html_url": "https://github.com/PingScientist/PastExamWeb_PHY/issues/123",
                "state": "open",
            },
        )

    client = GitHubIssuesClient(
        enabled=True,
        token="test-token",
        owner="PingScientist",
        repository="PastExamWeb_PHY",
        transport=httpx.MockTransport(handler),
    )
    issue = await client.create_issue(_report())

    request = captured["request"]
    payload = json.loads(request.content)
    assert str(request.url) == (
        "https://api.github.com/repos/PingScientist/PastExamWeb_PHY/issues"
    )
    assert request.headers["authorization"] == "Bearer test-token"
    assert request.headers["x-github-api-version"] == "2022-11-28"
    assert request.headers["user-agent"] == "PastExamWeb-PHY-Issue-Linker"
    assert payload["title"] == "預覽失敗"
    assert "<!-- pastexam-system-report:42 -->" in payload["body"]
    assert "private@example.com" not in payload["body"]
    assert "secret=value" not in payload["body"]
    assert "private query" not in payload["body"]
    assert issue.number == 123
    assert issue.state == "open"


@pytest.mark.asyncio
async def test_github_client_normalizes_api_failures_without_leaking_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            headers={"x-ratelimit-remaining": "0"},
            json={"message": "token test-token is invalid"},
        )

    client = GitHubIssuesClient(
        enabled=True,
        token="test-token",
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(GitHubIssueError, match="速率限制") as caught:
        await client.create_issue(_report())

    assert "test-token" not in caught.value.public_message


def test_github_issue_body_and_url_validation_are_repository_scoped():
    body = build_issue_body(_report())

    assert "點擊預覽後沒有反應" in body
    assert "private@example.com" not in body
    assert is_allowed_github_issue_url(
        "https://github.com/PingScientist/PastExamWeb_PHY/issues/9", 9
    )
    assert not is_allowed_github_issue_url(
        "https://github.com/other/repository/issues/9", 9
    )
    assert not is_allowed_github_issue_url(
        "https://github.com/PingScientist/PastExamWeb_PHY/issues/10", 9
    )
