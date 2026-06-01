"""
Database session management — async SQLAlchemy engine + session factory.
Uses dependency injection pattern for FastAPI endpoints.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import get_settings
from app.models import Base

settings = get_settings()

# ── Async Engine ──
engine = create_async_engine(
    settings.database_url,
    echo=False,        # Set True for SQL query logging during debug
    pool_size=5,
    max_overflow=10,
)

# ── Session Factory ──
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Create all tables on startup. In production, use Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a database session per request."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
