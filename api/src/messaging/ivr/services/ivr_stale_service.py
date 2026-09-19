"""Cierre de interacciones que nunca recibieron su evento terminal.

Red de seguridad independiente del transporte: Helena solo reintenta un webhook
ante errores de red, así que un despliegue o una caída de la API pierde los
eventos de esa ventana. Sin esto, esas llamadas quedarían abiertas para siempre
y su contacto congelado en `SENT`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from core.tools.config_tools import get_or_default
from messaging.contacts.repository.contact_repository import ContactRepository
from messaging.ivr.constants.helena_defaults import DEFAULT_STALE_MINUTES
from messaging.ivr.repository.ivr_interaction_repository import IvrInteractionRepository


def _stale_minutes() -> int:
    raw = get_or_default("IVR_STALE_MINUTES", DEFAULT_STALE_MINUTES)
    try:
        value = int(raw)
    except ValueError:
        return int(DEFAULT_STALE_MINUTES)
    return value if value > 0 else int(DEFAULT_STALE_MINUTES)


class IvrStaleService:

    def __init__(
        self, interaction_repo: IvrInteractionRepository, contact_repo: ContactRepository
    ) -> None:
        self._interactions = interaction_repo
        self._contacts = contact_repo

    async def run(self) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=_stale_minutes())
        stale = await self._interactions.find_stale_open(cutoff)

        closed = len(stale)
        if closed:
            now = datetime.now(timezone.utc)
            ids = [row.id for row in stale]
            await self._interactions.close_stale_bulk(ids, "STALE_TIMEOUT", now)

            contact_ids = list({row.contact_id for row in stale if row.contact_id is not None})
            if contact_ids:
                await self._contacts.mark_failed_if_sent_bulk(contact_ids)

            logger.warning(
                "[ivr_stale] %d interacciones cerradas por timeout (> %d min sin evento terminal)",
                closed,
                _stale_minutes(),
            )
        return closed


def make_ivr_stale_service(session: AsyncSession) -> IvrStaleService:
    return IvrStaleService(
        interaction_repo=IvrInteractionRepository(session),
        contact_repo=ContactRepository(session),
    )
