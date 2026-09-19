import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status

from core.config.logger import logger
from core.tools.config_tools import get_or_throw
from messaging.contacts.enums.contact_enums import ContactStatus
from messaging.contacts.repository.contact_repository import ContactRepository
from messaging.whatsapp.enums.whatsapp_enums import MessageDirection
from messaging.whatsapp.models.whatsapp_chat_model import WhatsAppChatModel
from messaging.whatsapp.models.whatsapp_message_model import WhatsAppMessageModel
from messaging.whatsapp.models.whatsapp_send_error_model import WhatsAppSendErrorModel
from messaging.whatsapp.repository.whatsapp_chat_repository import WhatsAppChatRepository
from messaging.whatsapp.repository.whatsapp_message_repository import WhatsAppMessageRepository
from messaging.whatsapp.repository.whatsapp_org_credentials_repository import WhatsAppOrgCredentialsRepository
from messaging.whatsapp.repository.whatsapp_send_error_repository import WhatsAppSendErrorRepository
from messaging.whatsapp.schemas.whatsapp_chat_schemas import WhatsAppMessageResponse
from messaging.whatsapp.services.whatsapp_assignment_service import WhatsAppAssignmentService
from messaging.whatsapp.websocket.connection_manager import whatsapp_ws_manager

_STATUS_MAP = {
    "sent": ContactStatus.SENT,
    "delivered": ContactStatus.DELIVERED,
    "read": ContactStatus.OPENED,
    "failed": ContactStatus.FAILED,
}


def _extract_content(message: dict[str, Any]) -> str | None:
    message_type = message.get("type")
    if message_type == "text":
        return message.get("text", {}).get("body")
    if message_type == "button":
        return message.get("button", {}).get("text")
    if message_type == "interactive":
        interactive = message.get("interactive", {})
        if "button_reply" in interactive:
            return interactive["button_reply"].get("title")
        if "list_reply" in interactive:
            return interactive["list_reply"].get("title")
    return None


def _from_timestamp(raw: str | None) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(int(raw), tz=timezone.utc)


def _unwrap_error(item: dict[str, Any]) -> dict[str, Any]:
    """La doc muestra el objeto de error envuelto en una clave `error` (forma de
    respuesta HTTP de la Graph API); dentro de un array `errors[]` de webhook algunos
    payloads reales lo traen así envuelto y otros ya vienen "planos" — se soporta
    cualquiera de las dos formas.
    """
    return item.get("error", item)


class WhatsAppWebhookService:

    def __init__(
        self,
        credentials_repo: WhatsAppOrgCredentialsRepository,
        contact_repo: ContactRepository,
        error_repo: WhatsAppSendErrorRepository,
        chat_repo: WhatsAppChatRepository,
        message_repo: WhatsAppMessageRepository,
        assignment_service: WhatsAppAssignmentService,
    ) -> None:
        self._credentials_repo = credentials_repo
        self._contact_repo = contact_repo
        self._error_repo = error_repo
        self._chat_repo = chat_repo
        self._message_repo = message_repo
        self._assignment_service = assignment_service

    def verify(self, mode: str | None, verify_token: str | None, challenge: str | None) -> str:
        expected = get_or_throw("WHATSAPP_CLOUD_VERIFY_TOKEN")
        if mode != "subscribe" or verify_token != expected or not challenge:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Verificación de webhook inválida")
        return challenge

    async def handle_event(self, body: dict[str, Any]) -> None:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                await self._handle_change(change.get("value", {}))

    async def _handle_change(self, value: dict[str, Any]) -> None:
        phone_number_id = value.get("metadata", {}).get("phone_number_id")
        if not phone_number_id:
            logger.debug("[whatsapp_webhook] evento sin phone_number_id, se ignora")
            return

        credentials = await self._credentials_repo.get_by_phone_number_id(phone_number_id)
        if credentials is None:
            logger.warning(
                "[whatsapp_webhook] phone_number_id sin organización configurada | phone_number_id=%s",
                phone_number_id,
            )
            return
        organization_id = credentials.organization_id

        # `contacts[]` es hermano de `messages[]` (no va anidado en cada mensaje) —
        # se arma un lookup por wa_id para poder actualizar el nombre de perfil del chat.
        profile_names = {
            contact.get("wa_id"): contact.get("profile", {}).get("name")
            for contact in value.get("contacts", [])
            if contact.get("wa_id")
        }

        for status_event in value.get("statuses", []):
            await self._handle_status(status_event)
        for message in value.get("messages", []):
            await self._handle_message(organization_id, message, profile_names.get(message.get("from")))

        # Confirmado en la doc de códigos de error: los errores de la API de la nube
        # también pueden llegar sueltos en `value.errors`, sin ir amarrados a un status
        # puntual (ej. problemas de cuenta/autorización) — se guardan sin contact_id/wamid.
        occurred_at = _from_timestamp(None)
        for error in value.get("errors", []):
            await self._persist_error(None, None, _unwrap_error(error), value, occurred_at)

    async def _handle_status(self, status_event: dict[str, Any]) -> None:
        wamid = status_event.get("id")
        raw_status = status_event.get("status")
        if not wamid or not raw_status:
            return

        new_status = _STATUS_MAP.get(raw_status)
        contact = await self._contact_repo.get_by_external_id(wamid)
        if contact is None:
            logger.warning("[whatsapp_webhook] contacto no encontrado para wamid=%s", wamid)
        elif new_status is not None:
            contact.status = new_status
            await self._contact_repo.update(contact)

        if raw_status != "failed":
            return

        occurred_at = _from_timestamp(status_event.get("timestamp"))
        contact_id = contact.id if contact is not None else None
        for error in status_event.get("errors", []):
            await self._persist_error(contact_id, wamid, _unwrap_error(error), status_event, occurred_at)

    async def _persist_error(
        self,
        contact_id: uuid.UUID | None,
        wamid: str | None,
        error: dict[str, Any],
        raw_payload: dict[str, Any],
        occurred_at: datetime,
    ) -> None:
        # Meta reintenta la entrega de un POST hasta 7 días si el servidor no respondió
        # 200 (batching/reintentos documentados) — hay que deduplicar, no asumir que cada
        # entrega es un evento nuevo.
        if wamid is not None:
            existing = await self._error_repo.get_by_wamid_and_code(wamid, error.get("code", 0))
            if existing is not None:
                return

        error_data = error.get("error_data") or {}
        await self._error_repo.add(
            WhatsAppSendErrorModel(
                contact_id=contact_id,
                wamid=wamid,
                error_code=error.get("code", 0),
                error_subcode=error.get("error_subcode"),
                error_type=error.get("type"),
                message=error.get("message", ""),
                details=error_data.get("details"),
                fbtrace_id=error.get("fbtrace_id"),
                raw_payload=raw_payload,
                occurred_at=occurred_at,
            )
        )

    async def _handle_message(
        self, organization_id: uuid.UUID, message: dict[str, Any], profile_name: str | None = None
    ) -> None:
        phone = message.get("from")
        wamid = message.get("id")
        if not phone:
            return

        # Meta reintenta la entrega de un POST hasta 7 días si el servidor no respondió
        # 200 — sin esto, un reintento duplicaría el mensaje en el hilo del agente.
        if wamid is not None and await self._message_repo.get_by_wamid(wamid) is not None:
            return

        chat = await self._chat_repo.get_by_org_and_phone(organization_id, phone)
        is_new_chat = chat is None
        if chat is None:
            debtor_contact = await self._contact_repo.get_latest_by_recipient_and_org(phone, organization_id)
            chat = await self._chat_repo.add(
                WhatsAppChatModel(
                    organization_id=organization_id,
                    phone=phone,
                    profile_name=profile_name,
                    debtor_id=debtor_contact.debtor_id if debtor_contact is not None else None,
                    portfolio_id=debtor_contact.portfolio_id if debtor_contact is not None else None,
                    campaign_id=debtor_contact.campaign_id if debtor_contact is not None else None,
                )
            )

        sent_at = _from_timestamp(message.get("timestamp"))
        chat.last_message_at = sent_at
        # El nombre de perfil puede cambiar — se actualiza al valor más reciente que
        # traiga Meta; si este mensaje no lo trae, se conserva el último conocido.
        if profile_name:
            chat.profile_name = profile_name
        chat = await self._chat_repo.update(chat)

        saved_message = await self._message_repo.add(
            WhatsAppMessageModel(
                chat_id=chat.id,
                direction=MessageDirection.INBOUND,
                wamid=wamid,
                message_type=message.get("type", "unknown"),
                content=_extract_content(message),
                raw_payload=message,
                sent_at=sent_at,
            )
        )

        if is_new_chat:
            chat = await self._assignment_service.assign(chat, organization_id)

        if chat.assigned_user_id is not None:
            payload = json.loads(
                WhatsAppMessageResponse.model_validate(saved_message).model_dump_json(by_alias=True)
            )
            await whatsapp_ws_manager.send_to_user(chat.assigned_user_id, "new_message", payload)
