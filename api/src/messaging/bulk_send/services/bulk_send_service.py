from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from app_platform.countries.enums.country_enums import UserDocumentType
from app_platform.countries.repository.country_repository import CountryRepository
from messaging.provider_credentials.services.provider_credential_service import MessagingProviderCredentialService
from billing.billing_status.services.billing_status_service import BillingStatusService
from core.config.logger import logger
from core.security.constants.permissions import PORTFOLIO_COMMUNICATIONS
from core.security.policies.security_policies import check_portfolio_org_access
from core.security.services.encrypt_service import encrypt_service
from identity.users.schemas.user_session_schema import UserSession
from messaging.bulk_send.schemas.bulk_send_schemas import BulkSendResponse
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.campaigns.schemas.batch_schemas import BatchStats, SendInput
from messaging.campaigns.services.batch_sender import BatchSender
from messaging.campaigns.utils.provider_utils import is_phone_channel, normalize_phone
from messaging.campaigns.utils.substitution_utils import build_sub
from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.models.channel_model import ChannelModel
from messaging.channels.repository.channel_repository import ChannelRepository
from messaging.templates.enums.template_enums import TemplateChannel
from messaging.templates.models.template_model import TemplateModel
from messaging.templates.repository.template_repository import TemplateRepository
from messaging.whatsapp.enums.whatsapp_enums import ChannelRequestStatus
from messaging.whatsapp.repository.whatsapp_org_credentials_repository import WhatsAppOrgCredentialsRepository
from messaging.whatsapp.repository.whatsapp_template_data_repository import WhatsAppTemplateDataRepository
from messaging.whatsapp.services.whatsapp_channel_request_service import WhatsAppChannelRequestService
from messaging.whatsapp.services.whatsapp_number_request_service import WhatsAppNumberRequestService
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository

_RESERVED_COLS = {"tipo_documento", "documento", "destinatario"}


class BulkSendService:

    def __init__(
        self,
        debtor_repo: DebtorRepository,
        channel_repo: ChannelRepository,
        template_repo: TemplateRepository,
        portfolio_repo: PortfolioRepository,
        campaign_repo: CampaignRepository,
        batch_sender: BatchSender,
        billing_status_service: BillingStatusService,
        whatsapp_credentials_repo: WhatsAppOrgCredentialsRepository,
        whatsapp_template_data_repo: WhatsAppTemplateDataRepository,
        whatsapp_channel_request_service: WhatsAppChannelRequestService,
        whatsapp_number_request_service: WhatsAppNumberRequestService,
    ) -> None:
        self._debtor_repo = debtor_repo
        self._channel_repo = channel_repo
        self._template_repo = template_repo
        self._portfolio_repo = portfolio_repo
        self._campaign_repo = campaign_repo
        self._country_repo = CountryRepository(portfolio_repo.session)
        self._credential_service = MessagingProviderCredentialService(portfolio_repo.session)
        self._batch_sender = batch_sender
        self._billing_status_service = billing_status_service
        self._whatsapp_credentials_repo = whatsapp_credentials_repo
        self._whatsapp_template_data_repo = whatsapp_template_data_repo
        self._whatsapp_channel_request_service = whatsapp_channel_request_service
        self._whatsapp_number_request_service = whatsapp_number_request_service

    async def process(
        self,
        portfolio_id: uuid.UUID,
        channel_id: uuid.UUID,
        rows: list[dict[str, str]],
        user_session: UserSession,
        template_id: uuid.UUID | None = None,
        body: str | None = None,
        subject: str | None = None,
    ) -> BulkSendResponse:
        portfolio = await self._portfolio_repo.get_by_id(portfolio_id)
        organization_id = await check_portfolio_org_access(user_session, portfolio, PORTFOLIO_COMMUNICATIONS)

        if await self._billing_status_service.is_blocked(organization_id):
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED,
                "Envíos bloqueados por factura vencida sin pagar. Realiza el pago para reanudarlos.",
            )

        channel = await self._channel_repo.get_by_id(channel_id)
        if channel is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Canal no encontrado")

        channel_name = channel.name

        if channel_name == ChannelName.EMAIL and not subject:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El campo 'subject' es obligatorio para envíos por EMAIL")

        if channel_name == ChannelName.WHATSAPP and body:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Para WhatsApp debes usar una plantilla guardada (templateId), no contenido inline")

        phone_number_id: str | None = None
        if channel_name == ChannelName.WHATSAPP:
            credentials = await self._whatsapp_credentials_repo.get_by_organization(organization_id)
            if credentials is None or not credentials.active:
                # Crea (o reutiliza) el ticket de soporte asignado a servicio al cliente
                # global, mismo patrón que la validación de documentos de empresa.
                await self._whatsapp_number_request_service.ensure_number_available(
                    organization_id, user_session.user_id
                )
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "Esta organización todavía no tiene un número de WhatsApp configurado. "
                    "Se generó una solicitud a soporte para provisionarlo.",
                )
            phone_number_id = credentials.phone_number_id

        template_body, template_subject, whatsapp_language = await self._resolve_template(
            portfolio_id, template_id, body, subject
        )

        manual_campaign = await self._campaign_repo.get_or_create_manual(
            portfolio_id=portfolio_id,
            channel_id=channel_id,
            channel_label=channel.label,
        )

        phone_prefix = None
        if is_phone_channel(channel_name):
            phone_prefix = await self._country_repo.get_phone_prefix(portfolio.country)
            if phone_prefix is None:
                logger.warning(
                    "[bulk_send] portafolio %s sin país/indicativo; se envía sin prefijo", portfolio_id
                )

        inputs, skipped, pending_approval = await self._build_inputs(
            rows=rows,
            template_body=template_body,
            template_subject=template_subject,
            organization_id=organization_id,
            portfolio_id=portfolio_id,
            channel=channel,
            campaign_id=manual_campaign.id,
            phone_prefix=phone_prefix,
        )

        if not inputs:
            return BulkSendResponse(
                total_sent=0,
                success_count=0,
                failure_count=0,
                unique_customers=0,
                skipped_rows=skipped,
                pending_approval_count=pending_approval,
            )

        stats: BatchStats = await self._batch_sender.process_batch(
            inputs,
            channel_name.value,
            phone_prefix=phone_prefix,
            campaign_name=manual_campaign.name,
            phone_number_id=phone_number_id,
            language=whatsapp_language,
            credential_service=self._credential_service,
            country=portfolio.country,
        )

        return BulkSendResponse(
            total_sent=stats.total_sent,
            success_count=stats.success_count,
            failure_count=stats.failure_count,
            unique_customers=stats.unique_customers,
            skipped_rows=skipped,
            pending_approval_count=pending_approval,
        )

    async def _resolve_template(
        self,
        portfolio_id: uuid.UUID,
        template_id: uuid.UUID | None,
        body: str | None,
        subject: str | None,
    ) -> tuple[str, str | None, str | None]:
        if template_id is not None:
            tpl: TemplateModel | None = await self._template_repo.get_by_id_and_portfolio(template_id, portfolio_id)
            if tpl is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Plantilla no encontrada")
            if tpl.channel == TemplateChannel.WHATSAPP:
                whatsapp_data = await self._whatsapp_template_data_repo.get_by_template_id(tpl.id)
                if whatsapp_data is None:
                    raise HTTPException(status.HTTP_404_NOT_FOUND, "Plantilla de WhatsApp no encontrada")
                return whatsapp_data.meta_name, None, whatsapp_data.language
            return tpl.body, tpl.subject or subject, None

        if body:
            return body, subject, None

        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Debes indicar 'templateId' o 'body'")

    async def _build_inputs(
        self,
        rows: list[dict[str, str]],
        template_body: str,
        template_subject: str | None,
        organization_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        channel: ChannelModel,
        campaign_id: uuid.UUID,
        phone_prefix: str | None = None,
    ) -> tuple[list[SendInput], int, int]:
        inputs: list[SendInput] = []
        seen_recipients: set[str] = set()
        skipped = 0
        pending_approval = 0
        is_whatsapp = channel.name == ChannelName.WHATSAPP

        # Resolver todos los deudores del archivo en una sola query en vez de una por fila
        # (un bulk send puede traer hasta 10k filas).
        doc_hashes = {
            encrypt_service.hash_document(row["documento"].strip())
            for row in rows
            if row.get("documento", "").strip()
        }
        debtors_by_hash = {
            debtor.document_number_hash: debtor
            for debtor in await self._debtor_repo.get_by_document_hashes(organization_id, list(doc_hashes))
        }

        # Mismo prefetch en batch para el gate de consentimiento de WhatsApp: evita un
        # SELECT de "ensure_case" por fila.
        case_status_cache: dict[str, ChannelRequestStatus] = {}
        if is_whatsapp:
            all_phones = list({
                (normalize_phone(row["destinatario"].strip(), phone_prefix) if phone_prefix else row["destinatario"].strip())
                for row in rows
                if row.get("destinatario", "").strip()
            })
            case_status_cache = await self._whatsapp_channel_request_service.get_existing_statuses(
                organization_id, all_phones
            )

        for row in rows:
            tipo_raw = row.get("tipo_documento", "").strip()
            documento = row.get("documento", "").strip()
            destinatario = row.get("destinatario", "").strip()

            if not destinatario:
                skipped += 1
                continue

            if destinatario in seen_recipients:
                skipped += 1
                continue

            try:
                doc_type = UserDocumentType(tipo_raw)
            except ValueError:
                logger.warning("[bulk_send] tipo_documento inválido '%s', fila omitida", tipo_raw)
                skipped += 1
                continue

            debtor_id: uuid.UUID | None = None
            if documento:
                doc_hash = encrypt_service.hash_document(documento)
                debtor = debtors_by_hash.get(doc_hash)
                if debtor is not None:
                    debtor_id = debtor.id
                else:
                    logger.warning("[bulk_send] deudor no encontrado tipo=%s", tipo_raw)

            if is_whatsapp:
                phone = normalize_phone(destinatario, phone_prefix) if phone_prefix else destinatario
                case_status = case_status_cache.get(phone)
                if case_status is None:
                    case_status = await self._whatsapp_channel_request_service.ensure_case(
                        organization_id, phone, debtor_id=debtor_id, origin_campaign_id=campaign_id
                    )
                    case_status_cache[phone] = case_status
                if case_status != ChannelRequestStatus.APPROVED:
                    pending_approval += 1
                    continue

            variables: dict[str, str] = {k: v for k, v in row.items() if k not in _RESERVED_COLS and v}
            sub = build_sub(variables) if variables else None

            seen_recipients.add(destinatario)
            inputs.append(
                SendInput(
                    recipient=destinatario,
                    content=template_body,
                    subject=template_subject,
                    debtor_id=debtor_id,
                    debtor_document=documento or None,
                    campaign_id=campaign_id,
                    organization_id=organization_id,
                    portfolio_id=portfolio_id,
                    snapshot_channel_id=channel.id,
                    snapshot_currency=channel.currency,
                    snapshot_unit_price=channel.unit_price,
                    sub=sub,
                )
            )

        return inputs, skipped, pending_approval
