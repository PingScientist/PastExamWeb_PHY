from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings


class WorkerSettings:
    """ARQ worker settings.

    The project currently has no background jobs registered.
    """

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = []

    max_jobs = 5
    job_timeout = 600
    keep_result = 86400


async def get_redis_pool():
    """Get Redis connection pool."""
    return await create_pool(WorkerSettings.redis_settings)
