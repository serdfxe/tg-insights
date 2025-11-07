import logging

from typing import Callable, Dict, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from db.models import Base
from db.repository import DatabaseRepo


Model = TypeVar("Model", bound=Base)
logger = logging.getLogger(__name__)


class UOW:
    def __init__(self, session_factory: Callable):
        self.session: AsyncSession | None = None
        self.session_factory = session_factory
        self._repositories: Dict[Type[Model], DatabaseRepo] = {}

    async def _next_session(self):
        if self.session is not None:
            await self.session.close()

        self.session = await self.session_factory.__anext__()

    async def __aenter__(self):
        await self._next_session()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            await self.session.close()

            self.session = None
            self._repositories.clear()

        return False

    async def get_repo(self, model: Type[Model]) -> DatabaseRepo[Model]:
        if model not in self._repositories:
            if self.session is None:
                await self._next_session()
            self._repositories[model] = DatabaseRepo(model, self.session)

        return self._repositories[model]

    async def commit(self):
        if self.session:
            await self.session.commit()

    async def rollback(self):
        if self.session:
            await self.session.rollback()


def get_uow():
    return UOW(session_factory=get_db_session())
