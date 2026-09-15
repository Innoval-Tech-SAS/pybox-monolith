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

    async def add_isolated(self, instance: T) -> None:
        """Inserta en un savepoint propio, sin refresh posterior.

        Un INSERT inválido (p. ej. dato demasiado largo) se aísla y no rompe la
        transacción del llamador. Usar solo cuando nadie necesita releer después los
        campos que genera la base de datos (ids, defaults) sobre ``instance``.
        """
        async with self.session.begin_nested():
            self.session.add(instance)
            await self.session.flush()

    async def add_many(self, instances: List[T]) -> Sequence[T]:
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def add_many_isolated(self, instances: List[T]) -> None:
        """Como `add_isolated`, pero para varias instancias a la vez: un solo
        `flush()` (SQLAlchemy agrupa los INSERT de la misma clase en un solo
        round trip vía "insertmany"), aislado en su propio savepoint, sin refresh.

        Usar cuando ninguna instancia necesita releerse después (mismo criterio que
        `add_isolated`) y todas son inserciones nuevas -- no reemplaza un upsert.
        """
        async with self.session.begin_nested():
            self.session.add_all(instances)
            await self.session.flush()

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
