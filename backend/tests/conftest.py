import asyncio
import os
import uuid
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from unittest.mock import AsyncMock

from app.core.config import settings
from app.main import app
from app.models.models import Archive, User
from app.utils.auth import get_password_hash

RUNTIME_DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
FORBIDDEN_DATABASE_NAMES = {"archive_db"}


def is_test_database_name(database_name: str | None) -> bool:
    normalized = str(database_name or "").strip().lower()
    return bool(normalized) and normalized not in FORBIDDEN_DATABASE_NAMES and (
        normalized.startswith("test_") or normalized.endswith("_test")
    )


def validate_test_database_url(
    test_database_url: str | None, runtime_database_url: str
) -> str:
    if not test_database_url:
        raise ValueError("TEST_DATABASE_URL must be explicitly configured")
    test_url = make_url(test_database_url)
    runtime_url = make_url(runtime_database_url)
    test_database_name = test_url.database or ""
    runtime_database_name = runtime_url.database or ""
    if test_url == runtime_url or test_database_name == runtime_database_name:
        raise ValueError("TEST_DATABASE_URL must not target the runtime database")
    if not is_test_database_name(test_database_name):
        raise ValueError("Test database name must start with 'test_' or end with '_test'")
    return test_database_name


def validate_connected_database_name(
    actual_database_name: str | None,
    configured_database_name: str,
    runtime_database_name: str,
) -> None:
    actual = str(actual_database_name or "").strip()
    if (
        actual != configured_database_name
        or actual == runtime_database_name
        or not is_test_database_name(actual)
    ):
        raise ValueError("Connected database does not match the isolated test database")


try:
    CONFIGURED_DATABASE_NAME = validate_test_database_url(
        TEST_DATABASE_URL, RUNTIME_DATABASE_URL
    )
except (TypeError, ValueError):
    pytest.exit(
        "Refusing to run backend tests without an explicit, isolated TEST_DATABASE_URL. "
        "The database name must start with 'test_' or end with '_test'.",
        returncode=2,
    )

DATABASE_URL = TEST_DATABASE_URL


@pytest.fixture(scope="session")
def event_loop() -> AsyncIterator[asyncio.AbstractEventLoop]:
    """Provide a single event loop for all async tests."""
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest_asyncio.fixture(autouse=True)
async def override_db_session(monkeypatch):
    """Swap engine per run to dodge asyncpg loop clashes."""
    engine = create_async_engine(
        DATABASE_URL,
        poolclass=NullPool,
        future=True,
    )
    session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with engine.connect() as connection:
        actual_database_name = await connection.scalar(text("SELECT current_database()"))
    try:
        validate_connected_database_name(
            actual_database_name,
            CONFIGURED_DATABASE_NAME,
            make_url(RUNTIME_DATABASE_URL).database or "",
        )
    except ValueError:
        await engine.dispose()
        pytest.fail("Connected database is not an isolated test database", pytrace=False)

    monkeypatch.setattr("app.db.session.engine", engine)
    monkeypatch.setattr("app.db.session.AsyncSessionLocal", session_maker)

    yield

    await engine.dispose()


@pytest.fixture()
def session_maker():
    from app.db.session import AsyncSessionLocal

    return AsyncSessionLocal


@pytest_asyncio.fixture
async def make_user(session_maker):
    """Factory fixture to create and cleanup test users."""
    created_ids: list[int] = []

    async def _make_user(**overrides):
        password = overrides.pop("password", "StrongPass123!")
        base = {
            "name": f"user-{uuid.uuid4().hex[:8]}",
            "email": f"user-{uuid.uuid4().hex[:8]}@example.com",
            "password_hash": get_password_hash(password),
            "is_local": True,
            "is_admin": False,
        }

        if "password_hash" in overrides:
            base["password_hash"] = overrides.pop("password_hash")

        base.update(overrides)

        async with session_maker() as session:
            user = User(**base)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        created_ids.append(user.id)

        class _TestUser:
            __slots__ = ("_model", "password")

            def __init__(self, model: User, password_plain: str):
                self._model = model
                self.password = password_plain

            def __getattr__(self, item):
                return getattr(self._model, item)

            @property
            def model(self) -> User:
                return self._model

        return _TestUser(user, password)

    yield _make_user

    if created_ids:
        async with session_maker() as session:
            await session.execute(
                delete(Archive).where(Archive.uploader_id.in_(created_ids))
            )
            await session.execute(delete(User).where(User.id.in_(created_ids)))
            await session.commit()


@pytest_asyncio.fixture()
async def client(monkeypatch) -> AsyncIterator[AsyncClient]:
    """Return an AsyncClient backed by the FastAPI app."""
    monkeypatch.setattr("app.main.init_db", AsyncMock())
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client
