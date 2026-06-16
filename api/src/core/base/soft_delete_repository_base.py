from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import select

from core.base.repository_base import RepositoryBase, T


class SoftDeleteRepositoryBase(RepositoryBase[T]):
    """
    Repository base for models that use SoftDeleteMixin.
    get_by_id / get_all exclude deleted records by default.
    Use the _including_deleted variants when admin access is needed.
    """

    async def get_by_id(self, id: object) -> Optional[T]:
        instance = await self.session.get(self.model_class, id)
        if instance is None or instance.deleted_at is not None:  # type: ignore[union-attr]
            return None
        return instance

    async def get_all(self) -> Sequence[T]:
        result = await self.session.execute(
            select(self.model_class).where(
                self.model_class.deleted_at.is_(None)  # type: ignore[union-attr]
            )
        )
        return result.scalars().all()

    async def delete(self, instance: T) -> T:
        attached = await self.session.merge(instance)
        attached.deleted_at = datetime.now(timezone.utc)  # type: ignore[union-attr]
        await self.session.flush()
        await self.session.refresh(attached)
        return attached

    async def restore(self, instance: T) -> T:
        attached = await self.session.merge(instance)
        attached.deleted_at = None  # type: ignore[union-attr]
        await self.session.flush()
        await self.session.refresh(attached)
        return attached

    async def get_by_id_including_deleted(self, id: object) -> Optional[T]:
        return await self.session.get(self.model_class, id)

    async def get_all_including_deleted(self) -> Sequence[T]:
        result = await self.session.execute(select(self.model_class))
        return result.scalars().all()
