import pytest

from app import worker


@pytest.mark.asyncio
async def test_get_redis_pool(monkeypatch):
    async def fake_create_pool(settings):
        return f"pool-for-{settings}"

    monkeypatch.setattr(worker, "create_pool", fake_create_pool)
    pool = await worker.get_redis_pool()
    assert pool == f"pool-for-{worker.WorkerSettings.redis_settings}"


def test_worker_has_no_registered_jobs():
    assert worker.WorkerSettings.functions == []
