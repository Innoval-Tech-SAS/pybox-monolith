from typing import Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class RepositoryBase(Generic[T]):
    model_class: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, instance: T) -> T:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def add_many(self, instances: List[T]) -> Sequence[T]:
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def get_by_id(self, id: object) -> Optional[T]:
        return await self.session.get(self.model_class, id)

    async def get_all(self) -> Sequence[T]:
        result = await self.session.execute(select(self.model_class))
        return result.scalars().all()

    async def update(self, instance: T) -> T:
        merged = await self.session.merge(instance)
        await self.session.flush()
        await self.session.refresh(merged)
        return merged

    async def delete(self, instance: T) -> None:
        attached = await self.session.merge(instance)
        await self.session.delete(attached)
        await self.session.flush()
