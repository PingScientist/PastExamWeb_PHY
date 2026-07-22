import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.models.models import SystemIssueReport


GITHUB_API_VERSION = "2022-11-28"
GITHUB_API_URL = "https://api.github.com"
GITHUB_USER_AGENT = "PastExamWeb-PHY-Issue-Linker"


class GitHubIssueError(RuntimeError):
    def __init__(self, public_message: str):
        super().__init__(public_message)
        self.public_message = public_message


@dataclass(frozen=True)
class GitHubIssue:
    number: int
    url: str
    state: str


def _plain_text(value: Any, *, limit: int) -> str:
    text = str(value or "").replace("\x00", "").strip()
    return text[:limit]


def is_allowed_github_issue_url(
    url: str | None,
    issue_number: int | None,
    *,
    owner: str | None = None,
    repository: str | None = None,
) -> bool:
    if not url or not issue_number:
        return False
    safe_owner = re.escape(owner or settings.GITHUB_REPOSITORY_OWNER)
    safe_repository = re.escape(repository or settings.GITHUB_REPOSITORY_NAME)
    match = re.fullmatch(
        rf"https://github\.com/{safe_owner}/{safe_repository}/issues/([1-9][0-9]*)",
        url,
    )
    return bool(match and int(match.group(1)) == issue_number)


def build_issue_body(report: SystemIssueReport) -> str:
    metadata = dict(report.metadata_json or {})
    route = metadata.get("route") if isinstance(metadata.get("route"), dict) else {}
    environment = [
        ("頁面", _plain_text(route.get("path"), limit=200)),
        ("瀏覽器資訊", _plain_text(metadata.get("userAgent"), limit=500)),
        ("平台", _plain_text(metadata.get("platform"), limit=100)),
        ("語言", _plain_text(metadata.get("language"), limit=50)),
        ("回報時間", _plain_text(metadata.get("timestamp"), limit=80)),
    ]
    environment_lines = [f"- {label}：{value}" for label, value in environment if value]
    sections = [
        f"<!-- pastexam-system-report:{report.id} -->",
        "## 系統問題",
        _plain_text(report.description, limit=2000),
        "## 類型",
        _plain_text(report.report_type, limit=40),
    ]
    if environment_lines:
        sections.extend(["## 環境資訊", "\n".join(environment_lines)])
    sections.append("---\n此 Issue 由清大物理考古系統建立。")
    return "\n\n".join(sections)


class GitHubIssuesClient:
    def __init__(
        self,
        *,
        enabled: bool | None = None,
        token: str | None = None,
        owner: str | None = None,
        repository: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.enabled = settings.GITHUB_ISSUES_ENABLED if enabled is None else enabled
        self.token = settings.GITHUB_TOKEN if token is None else token
        self.owner = owner or settings.GITHUB_REPOSITORY_OWNER
        self.repository = repository or settings.GITHUB_REPOSITORY_NAME
        self.transport = transport

    @property
    def configured(self) -> bool:
        return bool(self.enabled and self.token and self.owner and self.repository)

    async def create_issue(self, report: SystemIssueReport) -> GitHubIssue:
        if not self.configured:
            raise GitHubIssueError("GitHub Issue 串接尚未設定")

        endpoint = (
            f"{GITHUB_API_URL}/repos/{self.owner}/{self.repository}/issues"
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": GITHUB_USER_AGENT,
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }
        try:
            async with httpx.AsyncClient(
                headers=headers,
                timeout=httpx.Timeout(10.0),
                transport=self.transport,
            ) as client:
                response = await client.post(
                    endpoint,
                    json={
                        "title": _plain_text(report.title, limit=100),
                        "body": build_issue_body(report),
                    },
                )
        except httpx.TimeoutException as error:
            raise GitHubIssueError("GitHub API 連線逾時") from error
        except httpx.HTTPError as error:
            raise GitHubIssueError("暫時無法連線 GitHub API") from error

        if response.status_code not in {200, 201}:
            if response.status_code in {401, 403}:
                message = "GitHub credential 無效或權限不足"
                if response.headers.get("x-ratelimit-remaining") == "0":
                    message = "GitHub API 已達速率限制"
            elif response.status_code == 429:
                message = "GitHub API 已達速率限制"
            else:
                message = "GitHub Issue 建立失敗"
            raise GitHubIssueError(message)

        try:
            payload = response.json()
            number = int(payload["number"])
            url = str(payload["html_url"])
            state = str(payload.get("state") or "open").lower()
        except (KeyError, TypeError, ValueError) as error:
            raise GitHubIssueError("GitHub API 回傳格式無效") from error
        if state not in {"open", "closed"}:
            state = "open"
        if not is_allowed_github_issue_url(
            url,
            number,
            owner=self.owner,
            repository=self.repository,
        ):
            raise GitHubIssueError("GitHub API 回傳的 Issue 連結無效")
        return GitHubIssue(number=number, url=url, state=state)


def get_github_issues_client() -> GitHubIssuesClient:
    return GitHubIssuesClient()
