import uuid
from dataclasses import dataclass

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from messaging.whatsapp.models.whatsapp_chat_model import WhatsAppChatModel


@dataclass(frozen=True)
class OrgChatScope:
    """Qué hilos puede ver un usuario dentro de una organización concreta.

    Las reglas varían por organización: en una puede ser admin (ve todo) y en otra
    un agente (solo lo asignado). Por eso listar varias organizaciones a la vez no
    es un `IN (...)` de ids, sino un OR de condiciones independientes.
    """

    organization_id: uuid.UUID
    assigned_user_id: uuid.UUID | None = None
    portfolio_ids: list[uuid.UUID] | None = None


class WhatsAppChatRepository(SoftDeleteRepositoryBase[WhatsAppChatModel]):
    model_class = WhatsAppChatModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_org_and_phone(
        self, organization_id: uuid.UUID, phone: str
    ) -> WhatsAppChatModel | None:
        result = await self.session.execute(
            select(WhatsAppChatModel).where(
                WhatsAppChatModel.organization_id == organization_id,
                WhatsAppChatModel.phone == phone,
                WhatsAppChatModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_scopes(
        self,
        scopes: list[OrgChatScope],
        page: int,
        page_size: int,
        unrestricted: bool = False,
    ) -> tuple[list[WhatsAppChatModel], int]:
        """Lista hilos de una o varias organizaciones, aplicando a cada una sus propias
        reglas de visibilidad. `unrestricted` (usuario global) ignora los scopes y no
        filtra por organización.
        """
        query = select(WhatsAppChatModel).where(WhatsAppChatModel.deleted_at.is_(None))

        if not unrestricted:
            if not scopes:
                return [], 0
            conditions = []
            for scope in scopes:
                checks = [WhatsAppChatModel.organization_id == scope.organization_id]
                if scope.assigned_user_id is not None:
                    checks.append(WhatsAppChatModel.assigned_user_id == scope.assigned_user_id)
                # None = sin restricción (admin de la org o usuario global); una lista
                # (incluso vacía) acota a los portafolios que el agente tiene asignados
                # en accesos_usuario_portafolio — los hilos sin portafolio resuelto
                # (NULL) quedan fuera para agentes no-admin, ver
                # whatsapp_chat_service._get_chat_for_user.
                if scope.portfolio_ids is not None:
                    checks.append(WhatsAppChatModel.portfolio_id.in_(scope.portfolio_ids))
                conditions.append(and_(*checks))
            query = query.where(or_(*conditions))

        total: int = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        ) or 0
        result = await self.session.execute(
            query.order_by(WhatsAppChatModel.last_message_at.desc().nullslast())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_least_loaded_user(self, candidate_user_ids: list[uuid.UUID]) -> uuid.UUID | None:
        """Entre los agentes candidatos, el que tiene menos hilos abiertos asignados
        actualmente. Empate: el primero por `id_usuario` (orden estable)."""
        if not candidate_user_ids:
            return None
        result = await self.session.execute(
            select(WhatsAppChatModel.assigned_user_id, func.count())
            .where(
                WhatsAppChatModel.assigned_user_id.in_(candidate_user_ids),
                WhatsAppChatModel.deleted_at.is_(None),
            )
            .group_by(WhatsAppChatModel.assigned_user_id)
        )
        counts = dict(result.all())
        return min(sorted(candidate_user_ids, key=str), key=lambda uid: counts.get(uid, 0))
