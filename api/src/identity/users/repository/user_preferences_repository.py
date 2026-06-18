import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.repository_base import RepositoryBase
from identity.users.models.user_preferences_model import UserPreferencesModel


class UserPreferencesRepository(RepositoryBase[UserPreferencesModel]):
    model_class = UserPreferencesModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserPreferencesModel | None:
        result = await self.session.execute(
            select(UserPreferencesModel).where(UserPreferencesModel.user_id == user_id)
        )
        return result.scalars().first()

    async def dismiss_tour(self, user_id: uuid.UUID, tour_key: str) -> UserPreferencesModel:
        prefs = await self.get_by_user_id(user_id)
        if prefs is None:
            prefs = UserPreferencesModel(user_id=user_id, dismissed_tours=[tour_key])
            return await self.add(prefs)
        if tour_key not in prefs.dismissed_tours:
            prefs.dismissed_tours = list(prefs.dismissed_tours) + [tour_key]
            return await self.update(prefs)
        return prefs
