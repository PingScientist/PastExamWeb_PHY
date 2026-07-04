import os
import subprocess
import unicodedata
from datetime import datetime, timezone
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from sqlalchemy import inspect, text
import yaml
from sqlmodel import SQLModel, func, select

from app.core.config import settings
from app.db.session import AsyncSessionLocal, engine
from app.models.models import Course, CourseCategory, CourseCategoryConfig, Meme, User
from app.utils.auth import get_password_hash

SEED_DATA_PATH = Path(__file__).with_name("seed_data.yaml")
DEFAULT_CATEGORY_CONFIGS = [
    ("fundamental", "基礎必修", "基礎", "pi pi-fw pi-book"),
    ("required", "專業必修", "必修", "pi pi-fw pi-compass"),
    ("experience", "實驗課程", "實驗", "pi pi-fw pi-sparkles"),
    ("optional", "專業選修", "選修", "pi pi-fw pi-book"),
    ("graduate", "研究所", "研究所", "pi pi-fw pi-graduation-cap"),
    ("math-department", "戳戳數學系", "數學", "pi pi-fw pi-calculator"),
]
COURSE_CATEGORY_BADGE_COLOR_DEFAULT = "blue"


@lru_cache(maxsize=1)
def load_seed_data():
    with SEED_DATA_PATH.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _seed_course_key(course: Course) -> tuple[str, str]:
    category = getattr(course.category, "value", course.category)
    return (str(category), unicodedata.normalize("NFKC", course.name))


async def sync_course_catalog(session):
    seed_courses = [
        (
            course["category"],
            unicodedata.normalize("NFKC", course["name"]),
        )
        for course in load_seed_data().get("courses", [])
    ]

    result = await session.execute(select(Course))
    existing_courses = result.scalars().all()
    courses_by_key: dict[tuple[str, str], list[Course]] = {}
    for course in existing_courses:
        courses_by_key.setdefault(_seed_course_key(course), []).append(course)

    changed = False
    seed_order_by_key = {}
    category_positions = defaultdict(int)
    for category_name, course_name in seed_courses:
        category = CourseCategory[category_name]
        seed_order_by_key[(category.value, course_name)] = category_positions[category.value]
        category_positions[category.value] += 1

    active_courses_by_category = defaultdict(list)
    for course in existing_courses:
        if course.deleted_at is None:
            category = getattr(course.category, "value", course.category)
            active_courses_by_category[category].append(course)

    should_initialize_order = {
        category: all(course.order_index == 0 for course in courses)
        for category, courses in active_courses_by_category.items()
    }

    for category_name, course_name in seed_courses:
        category = CourseCategory[category_name]
        key = (category.value, course_name)
        matching_courses = courses_by_key.get(key, [])
        if matching_courses:
            primary, *duplicates = matching_courses
            if primary.deleted_at is not None:
                primary.deleted_at = None
                changed = True
            if should_initialize_order.get(category.value, True):
                expected_order = seed_order_by_key[key]
                if primary.order_index != expected_order:
                    primary.order_index = expected_order
                    changed = True
            for duplicate in duplicates:
                if duplicate.deleted_at is None:
                    duplicate.deleted_at = datetime.now(timezone.utc)
                    changed = True
            continue

        session.add(
            Course(
                name=course_name,
                category=category.value,
                order_index=seed_order_by_key[key],
            )
        )
        changed = True

    if changed:
        await session.commit()


async def sync_course_categories(session):
    result = await session.execute(select(CourseCategoryConfig))
    existing_by_key = {category.key: category for category in result.scalars().all()}
    changed = False

    for order_index, (key, name, label, icon) in enumerate(DEFAULT_CATEGORY_CONFIGS):
        category = existing_by_key.get(key)
        if category:
            if not category.name:
                category.name = name
                changed = True
            if not category.label:
                category.label = label
                changed = True
            if not category.icon:
                category.icon = icon
                changed = True
            if category.order_index is None:
                category.order_index = order_index
                changed = True
            if not category.is_active:
                category.is_active = True
                changed = True
            continue

        session.add(
            CourseCategoryConfig(
                key=key,
                name=name,
                label=label,
                icon=icon,
                order_index=order_index,
                is_active=True,
            )
        )
        changed = True

    if changed:
        await session.commit()


async def _ensure_course_category_badge_color_column() -> None:
    async with engine.begin() as conn:
        has_table = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("course_category_configs")
        )
        if not has_table:
            return

        columns = await conn.run_sync(
            lambda sync_conn: {
                column["name"]
                for column in inspect(sync_conn).get_columns("course_category_configs")
            }
        )
        if "badge_color" in columns:
            return

        await conn.execute(
            text(
                "ALTER TABLE course_category_configs ADD COLUMN IF NOT EXISTS badge_color VARCHAR"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE course_category_configs ALTER COLUMN badge_color SET DEFAULT :default_color"
            ),
            {"default_color": COURSE_CATEGORY_BADGE_COLOR_DEFAULT},
        )
        await conn.execute(
            text(
                "UPDATE course_category_configs SET badge_color = :default_color WHERE badge_color IS NULL"
            ),
            {"default_color": COURSE_CATEGORY_BADGE_COLOR_DEFAULT},
        )


async def init_db():
    # Run Alembic migrations instead of create_all
    try:
        # Run alembic upgrade head to apply all migrations
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Alembic migration failed: {result.stderr}")
            # Fallback to create_all if migration fails
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
                await conn.commit()
        else:
            print("Database migrations applied successfully")
    except Exception as e:
        print(f"Error running migrations: {e}")
        # Fallback to create_all
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            await conn.commit()

    await _ensure_course_category_badge_color_column()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.name == settings.DEFAULT_ADMIN_NAME)
        )
        admin_user = result.scalar_one_or_none()

        if admin_user and getattr(admin_user, "deleted_at", None) is not None:
            admin_user.deleted_at = None
            admin_user.password_hash = get_password_hash(
                settings.DEFAULT_ADMIN_PASSWORD
            )
            admin_user.is_local = True
            admin_user.is_admin = True
            await session.commit()
            await session.refresh(admin_user)
        elif not admin_user:
            admin_user = User(
                name=settings.DEFAULT_ADMIN_NAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                is_local=True,
                is_admin=True,
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

        await sync_course_categories(session)
        await sync_course_catalog(session)

        result = await session.execute(select(func.count()).select_from(Meme))
        count = result.scalar()
        if count == 0:
            seed_data = load_seed_data()
            initial_memes = [
                Meme(
                    content=meme["content"],
                    language=meme["language"],
                )
                for meme in seed_data.get("memes", [])
            ]
            session.add_all(initial_memes)
            await session.commit()


async def get_session():
    """
    Database dependency for FastAPI endpoints.
    """
    async with AsyncSessionLocal() as session:
        yield session
