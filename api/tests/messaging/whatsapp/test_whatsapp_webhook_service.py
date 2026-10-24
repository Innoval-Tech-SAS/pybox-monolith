"""Tests del webhook entrante de WhatsApp Cloud API (ver whatsapp_webhook_service.py).
Meta reintenta la entrega de un POST hasta 7 días si no se respondió 200 -- el
riesgo real es que un reintento duplique el mensaje en el hilo del agente y vuelva
a emitir por WebSocket, o que reasigne un chat que ya tenía agente. También se
cubre que un `phone_number_id` sin organización configurada no tumbe el webhook
completo (Meta puede reintentar entregas a números que la org desactivó).

Unitarios puros: todos los repositorios y el servicio de asignación van mockeados;
no se toca la base de datos real.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from messaging.whatsapp.enums.whatsapp_enums import MessageDirection
from messaging.whatsapp.models.whatsapp_chat_model import WhatsAppChatModel
from messaging.whatsapp.models.whatsapp_message_model import WhatsAppMessageModel
from messaging.whatsapp.services import whatsapp_webhook_service as webhook_module
from messaging.whatsapp.services.whatsapp_webhook_service import WhatsAppWebhookService


def build_webhook_body(
    phone_number_id: str, *, wamid: str, phone: str, text: str = "hola"
) -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {"phone_number_id": phone_number_id},
                            "contacts": [
                                {"wa_id": phone, "profile": {"name": "Juan Deudor"}}
                            ],
                            "messages": [
                                {
                                    "id": wamid,
                                    "from": phone,
                                    "timestamp": "1750000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }


def build_service(
    *,
    credentials_repo=None,
    contact_repo=None,
    error_repo=None,
    chat_repo=None,
    message_repo=None,
    assignment_service=None,
) -> WhatsAppWebhookService:
    return WhatsAppWebhookService(
        credentials_repo=credentials_repo or MagicMock(),
        contact_repo=contact_repo or MagicMock(),
        error_repo=error_repo or MagicMock(),
        chat_repo=chat_repo or MagicMock(),
        message_repo=message_repo or MagicMock(),
        assignment_service=assignment_service or MagicMock(),
    )


class TestHandleMessageDeduplicatesByWamid:
    async def test_retried_wamid_does_not_create_second_message_or_emit_again(self):
        organization_id = uuid.uuid4()
        agent_id = uuid.uuid4()
        phone_number_id = "1234567890"
        phone = "573001112233"
        wamid = "wamid.ABC123"

        credentials_repo = MagicMock()
        credentials_repo.get_by_phone_number_id = AsyncMock(
            return_value=MagicMock(organization_id=organization_id)
        )

        contact_repo = MagicMock()
        contact_repo.get_latest_by_recipient_and_org = AsyncMock(return_value=None)

        chat = WhatsAppChatModel(
            id=uuid.uuid4(), organization_id=organization_id, phone=phone
        )
        chat_repo = MagicMock()
        chat_repo.get_by_org_and_phone = AsyncMock(return_value=None)
        chat_repo.add = AsyncMock(return_value=chat)
        chat_repo.update = AsyncMock(side_effect=lambda c: c)

        saved_message = WhatsAppMessageModel(
            id=uuid.uuid4(),
            chat_id=chat.id,
            direction=MessageDirection.INBOUND,
            wamid=wamid,
            message_type="text",
            content="hola",
            raw_payload={},
            sent_at=datetime.now(timezone.utc),
        )
        message_repo = MagicMock()
        # 1er intento: no existe el wamid -> se crea. 2do intento (reintento de Meta
        # con el mismo wamid): ya existe -> debe cortar antes de crear nada más.
        message_repo.get_by_wamid = AsyncMock(side_effect=[None, saved_message])
        message_repo.add = AsyncMock(return_value=saved_message)

        async def fake_assign(chat_arg, _org_id):
            chat_arg.assigned_user_id = agent_id
            return chat_arg

        assignment_service = MagicMock()
        assignment_service.assign = AsyncMock(side_effect=fake_assign)

        service = build_service(
            credentials_repo=credentials_repo,
            contact_repo=contact_repo,
            chat_repo=chat_repo,
            message_repo=message_repo,
            assignment_service=assignment_service,
        )
        body = build_webhook_body(phone_number_id, wamid=wamid, phone=phone)

        with patch.object(
            webhook_module.whatsapp_ws_manager, "send_to_user", new_callable=AsyncMock
        ) as mock_send:
            await service.handle_event(body)  # entrega original
            await service.handle_event(body)  # reintento de Meta, mismo wamid

        assert message_repo.add.call_count == 1
        assert mock_send.call_count == 1


class TestHandleMessageReusesExistingChatWithoutReassigning:
    async def test_second_message_same_phone_reuses_chat_and_does_not_call_assign_again(
        self,
    ):
        organization_id = uuid.uuid4()
        agent_id = uuid.uuid4()
        phone_number_id = "1234567890"
        phone = "573001112233"

        credentials_repo = MagicMock()
        credentials_repo.get_by_phone_number_id = AsyncMock(
            return_value=MagicMock(organization_id=organization_id)
        )

        contact_repo = MagicMock()
        contact_repo.get_latest_by_recipient_and_org = AsyncMock(return_value=None)

        existing_chat = WhatsAppChatModel(
            id=uuid.uuid4(),
            organization_id=organization_id,
            phone=phone,
            assigned_user_id=agent_id,
        )
        chat_repo = MagicMock()
        # 1er mensaje: no hay chat todavía -> se crea. 2do: ya existe -> se reutiliza.
        chat_repo.get_by_org_and_phone = AsyncMock(side_effect=[None, existing_chat])
        chat_repo.add = AsyncMock(return_value=existing_chat)
        chat_repo.update = AsyncMock(side_effect=lambda c: c)

        def fake_message_add(message: WhatsAppMessageModel) -> WhatsAppMessageModel:
            # Simula lo que hace el repo real (RepositoryBase.add): asigna el id al
            # guardar -- sin esto, WhatsAppMessageResponse.model_validate revienta más
            # abajo porque `id` es requerido y quedaría en None.
            message.id = uuid.uuid4()
            return message

        message_repo = MagicMock()
        message_repo.get_by_wamid = AsyncMock(
            return_value=None
        )  # wamids distintos cada vez
        message_repo.add = AsyncMock(side_effect=fake_message_add)

        assignment_service = MagicMock()
        assignment_service.assign = AsyncMock(return_value=existing_chat)

        service = build_service(
            credentials_repo=credentials_repo,
            contact_repo=contact_repo,
            chat_repo=chat_repo,
            message_repo=message_repo,
            assignment_service=assignment_service,
        )
        body_1 = build_webhook_body(phone_number_id, wamid="wamid.first", phone=phone)
        body_2 = build_webhook_body(phone_number_id, wamid="wamid.second", phone=phone)

        with patch.object(
            webhook_module.whatsapp_ws_manager, "send_to_user", new_callable=AsyncMock
        ):
            await service.handle_event(body_1)  # chat nuevo -> se asigna
            await service.handle_event(body_2)  # mismo chat -> NO se reasigna

        assert assignment_service.assign.call_count == 1
        assert message_repo.add.call_count == 2


class TestHandleChangeUnknownPhoneNumberId:
    async def test_unconfigured_phone_number_id_is_ignored_without_raising(self):
        credentials_repo = MagicMock()
        # Ninguna organización tiene configurado este phone_number_id.
        credentials_repo.get_by_phone_number_id = AsyncMock(return_value=None)

        chat_repo = MagicMock()
        chat_repo.get_by_org_and_phone = AsyncMock()
        message_repo = MagicMock()
        message_repo.get_by_wamid = AsyncMock()

        service = build_service(
            credentials_repo=credentials_repo,
            chat_repo=chat_repo,
            message_repo=message_repo,
        )
        body = build_webhook_body(
            "phone-number-id-sin-organizacion", wamid="wamid.x", phone="573000000000"
        )

        # No debe lanzar ninguna excepción -- el evento se ignora en silencio.
        await service.handle_event(body)

        chat_repo.get_by_org_and_phone.assert_not_called()
        message_repo.get_by_wamid.assert_not_called()
