from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.api.services.archives import get_archive_submission_statistics
from app.api.services.submission_statistics import (
    SUBMISSION_RANGE_CONFIG,
    align_product_bucket,
    build_submission_statistics,
    get_submission_statistics_window,
)


NOW = datetime(2026, 7, 15, 4, 23, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("range_key", "bucket_minutes", "bucket_count"),
    [
        ("24h", 10, 144),
        ("48h", 20, 144),
        ("72h", 30, 144),
        ("7d", 240, 42),
        ("30d", 720, 60),
        ("90d", 1440, 90),
    ],
)
def test_submission_statistics_keeps_fixed_bucket_contract(
    range_key, bucket_minutes, bucket_count
):
    _, _, _, first_start, _ = get_submission_statistics_window(range_key, NOW)
    result = build_submission_statistics(
        range_key=range_key,
        counts_by_bucket_start={
            first_start: 2,
            first_start + timedelta(minutes=bucket_minutes): 3,
        },
        now=NOW,
    )

    assert len(result.points) == bucket_count
    assert result.bucket_minutes == bucket_minutes
    assert result.summary.total == 5
    assert result.summary.peak == 3
    assert result.summary.average == round(5 / bucket_count, 1)
    assert sum(point.count for point in result.points) == result.summary.total
    assert all(point.end - point.start == timedelta(minutes=bucket_minutes) for point in result.points)


def test_half_open_bucket_boundaries_do_not_overlap():
    bucket_minutes = SUBMISSION_RANGE_CONFIG["24h"][1]
    start = align_product_bucket(NOW, bucket_minutes)

    assert align_product_bucket(start, bucket_minutes) == start
    assert align_product_bucket(
        start + timedelta(minutes=bucket_minutes) - timedelta(microseconds=1), bucket_minutes
    ) == start
    assert align_product_bucket(
        start + timedelta(minutes=bucket_minutes), bucket_minutes
    ) == start + timedelta(minutes=bucket_minutes)


@pytest.mark.parametrize(
    "value",
    [
        datetime(2026, 7, 31, 23, 59, tzinfo=timezone.utc),
        datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc),
        datetime(2026, 12, 31, 23, 59, tzinfo=timezone.utc),
        datetime(2027, 1, 1, 0, 0, tzinfo=timezone.utc),
    ],
)
def test_bucket_alignment_handles_day_month_and_year_boundaries(value):
    aligned = align_product_bucket(value, 10)
    assert aligned <= value < aligned + timedelta(minutes=10)


def test_current_partial_bucket_is_present_without_future_buckets():
    result = build_submission_statistics(
        range_key="24h",
        counts_by_bucket_start={align_product_bucket(NOW, 10): 1},
        now=NOW,
    )

    assert result.points[-1].start == align_product_bucket(NOW, 10)
    assert result.points[-1].count == 1
    assert result.points[-1].start <= NOW < result.points[-1].end
    assert result.range_end == result.points[-1].end


def test_daily_bucket_uses_product_timezone_midnight():
    local_day = datetime(2026, 7, 15, 0, 5, tzinfo=timezone(timedelta(hours=8)))
    aligned = align_product_bucket(local_day, 24 * 60)

    assert aligned == datetime(2026, 7, 14, 16, 0, tzinfo=timezone.utc)


class _RowsResult:
    def __init__(self, rows=()):
        self._rows = rows

    def all(self):
        return list(self._rows)


class _FakeSession:
    def __init__(self, rows=()):
        self.rows = rows
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return _RowsResult(self.rows)


class _User:
    def __init__(self, is_admin):
        self.is_admin = is_admin


@pytest.mark.asyncio
async def test_submission_statistics_requires_admin():
    with pytest.raises(HTTPException) as exc_info:
        await get_archive_submission_statistics(
            mode="time",
            range_key="24h",
            current_user=_User(False),
            db=_FakeSession(),
        )
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize(("mode", "range_key"), [("other", "24h"), ("time", "30d")])
async def test_submission_statistics_rejects_invalid_mode_range_pairs(mode, range_key):
    with pytest.raises(HTTPException) as exc_info:
        await get_archive_submission_statistics(
            mode=mode,
            range_key=range_key,
            current_user=_User(True),
            db=_FakeSession(),
        )
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_submission_statistics_admin_response_is_aggregated_and_bounded():
    session = _FakeSession()
    result = await get_archive_submission_statistics(
        mode="time",
        range_key="24h",
        current_user=_User(True),
        db=session,
    )

    assert result.mode == "time"
    assert result.range == "24h"
    assert result.timezone == "Asia/Taipei"
    assert len(result.points) == 144
    assert result.summary.model_dump() == {"total": 0, "peak": 0, "average": 0.0}
    assert len(session.statements) == 1
    statement = str(session.statements[0])
    assert "archive_submissions.created_at >=" in statement
    assert "archive_submissions.created_at <" in statement
    assert "GROUP BY" in statement
