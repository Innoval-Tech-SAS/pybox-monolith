import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from identity.organizations.models.organization_model import OrganizationModel

# Prefijo del dominio en la clave del objeto (`<dominio>/<dueno>/<uuid><ext>`) para los
# documentos de verificación de una entidad (fiscal, mercantil, representante). Reemplaza
# a `DocumentOwnerScope.ORGANIZATION`, que desapareció junto con la asociación polimórfica.
ORGANIZATION_DOCUMENT_STORAGE_DOMAIN = "entidad"


class OrganizationRepository(SoftDeleteRepositoryBase[OrganizationModel]):
    model_class = OrganizationModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_ids(self, ids: list[uuid.UUID]) -> Sequence[OrganizationModel]:
        if not ids:
            return []
        result = await self.session.execute(
            select(OrganizationModel).where(
                OrganizationModel.id.in_(ids),
                OrganizationModel.deleted_at.is_(None),
            )
        )
        return result.scalars().all()
