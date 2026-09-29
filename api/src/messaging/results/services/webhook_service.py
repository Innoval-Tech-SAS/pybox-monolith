from core.config.logger import logger
from messaging.contacts.enums.contact_enums import ContactStatus
from messaging.contacts.repository.contact_repository import ContactRepository


class WebhookService:
    def __init__(self, repo: ContactRepository) -> None:
        self._repo = repo

    async def handle_event(self, message_id: str, event: str) -> None:
        if not message_id:
            logger.debug(
                "[results_webhook] evento sin id (envío desde el sitio web), event=%s",
                event,
            )
            return

        try:
            new_status = ContactStatus(event.upper())
        except ValueError:
            logger.warning(
                "[results_webhook] evento desconocido=%s id=%s", event, message_id
            )
            return

        contact = await self._repo.get_by_external_id(message_id)
        if contact is None:
            logger.warning(
                "[results_webhook] contacto no encontrado para id=%s", message_id
            )
            return

        contact.status = new_status
        await self._repo.update(contact)
