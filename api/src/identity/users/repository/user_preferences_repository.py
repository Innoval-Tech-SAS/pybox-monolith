import uuid

from sqlalchemy import select

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from identity.users.models.user_preferences_model import UserPreferencesModel


class UserPreferencesRepository(SoftDeleteRepositoryBase[UserPreferencesModel]):
    model_class = UserPreferencesModel

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserPreferencesModel | None:
        result = await self.session.execute(
            select(UserPreferencesModel).where(UserPreferencesModel.user_id == user_id)
        )
        return result.scalars().first()

    async def dismiss_tour(
        self, user_id: uuid.UUID, tour_key: str
    ) -> UserPreferencesModel:
        prefs = await self.get_by_user_id(user_id)
        if prefs is None:
            prefs = UserPreferencesModel(user_id=user_id, dismissed_tours=[tour_key])
            return await self.add(prefs)
        if tour_key not in prefs.dismissed_tours:
            prefs.dismissed_tours = list(prefs.dismissed_tours) + [tour_key]
            return await self.update(prefs)
        return prefs

    async def restore_tour(
        self, user_id: uuid.UUID, tour_key: str
    ) -> UserPreferencesModel | None:
        prefs = await self.get_by_user_id(user_id)
        if prefs is None or tour_key not in prefs.dismissed_tours:
            return prefs
        prefs.dismissed_tours = [
            key for key in prefs.dismissed_tours if key != tour_key
        ]
        return await self.update(prefs)

    async def restore_all_tours(
        self, user_id: uuid.UUID
    ) -> UserPreferencesModel | None:
        prefs = await self.get_by_user_id(user_id)
        if prefs is None or not prefs.dismissed_tours:
            return prefs
        prefs.dismissed_tours = []
        return await self.update(prefs)
