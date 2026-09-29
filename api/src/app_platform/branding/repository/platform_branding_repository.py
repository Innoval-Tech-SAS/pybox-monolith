"""Acceso a datos de la configuración de marca global (fila única)."""

from typing import Optional

from sqlalchemy import select

from app_platform.branding.models.platform_branding_model import PlatformBrandingModel
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase


class PlatformBrandingRepository(SoftDeleteRepositoryBase[PlatformBrandingModel]):
    model_class = PlatformBrandingModel

    async def get_singleton(self) -> Optional[PlatformBrandingModel]:
        """La fila la crea la migración: en operación normal siempre hay exactamente
        una. `None` solo es posible si a alguien se le ocurrió borrarla a mano."""
        result = await self.session.execute(select(PlatformBrandingModel).limit(1))
        return result.scalars().first()
