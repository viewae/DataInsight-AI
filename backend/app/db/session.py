"""Async SQLAlchemy session — requires `requirements-database.txt` (installed in Docker)."""

from collections.abc import AsyncGenerator

try:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "Install database dependencies: pip install -r requirements-database.txt"
    ) from e

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
