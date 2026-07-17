"""
Database engine/session setup (SQLAlchemy 2.0, async).
Works with SQLite (local dev) or PostgreSQL (production) via DATABASE_URL.
"""

import ssl
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DATABASE_URL, IS_POSTGRES
from models import Base

_connect_args = {}
if IS_POSTGRES:
    _connect_args["ssl"] = ssl.create_default_context()

engine = create_async_engine(
    DATABASE_URL, echo=False, future=True, connect_args=_connect_args
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables if they don't already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session():
    """Usage: `async with get_session() as session: ...`"""
    async with SessionLocal() as session:
        yield session
