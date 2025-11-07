import uuid
from typing import Generic, TypeVar

from sqlalchemy import BinaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Base

Model = TypeVar("Model", bound=Base)


class DatabaseRepo(Generic[Model]):
    """Repository for performing database queries."""

    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict) -> Model:
        """Создает новую запись в базе данных."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get(self, pk: uuid.UUID) -> Model | None:
        """Получает запись по первичному ключу."""
        return await self.session.get(self.model, pk)

    async def filter(
        self,
        *expressions: BinaryExpression,
    ) -> list[Model]:
        """Фильтрует записи по условиям."""
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        result = await self.session.scalars(query)
        return list(result)

    async def update(self, instance: Model, data: dict) -> Model:
        """Обновляет существующую запись."""
        for key, value in data.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, pk: uuid.UUID) -> None:
        """Удаляет запись по первичному ключу."""
        instance = await self.session.get(self.model, pk)
        if instance is not None:
            await self.session.delete(instance)
            await self.session.flush()

    async def delete_instance(self, instance: Model) -> None:
        """Удаляет конкретный экземпляр."""
        await self.session.delete(instance)
        await self.session.flush()
