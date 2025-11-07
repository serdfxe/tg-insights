from collections.abc import AsyncGenerator
import logging

from sqlalchemy import exc
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import DB_URL


logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(DB_URL, future=True, poolclass=NullPool)
    factory = async_sessionmaker(engine)

    async with factory() as session:
        yield session
