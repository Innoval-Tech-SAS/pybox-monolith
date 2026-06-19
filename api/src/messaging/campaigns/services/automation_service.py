from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.schema_manager.services.dml_service import DmlService
from billing.billing_status.services.billing_status_service import BillingStatusService
from billing.invoices.repository.invoice_repository import InvoiceRepository
from core.config.logger import logger
from messaging.campaigns.enums.campaign_enums import CampaignStatus, Periodicity
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.repositories.campaign_repositories import CampaignRepository
from messaging.campaigns.repositories.campaign_result_repository import CampaignResultRepository
from messaging.campaigns.repositories.campaign_time_repository import CampaignTimeRepository
from messaging.campaigns.schemas.batch_schemas import BatchStats, SendInput
from messaging.campaigns.services.batch_sender import BatchSender
from messaging.campaigns.utils.calculate_next import calculate_next_execution
from messaging.channels.repositories.channel_repository import ChannelRepository
from messaging.contacts.repositories.contact_repository import ContactRepository
from messaging.dispatcher import MessageDispatcher
from receivables.segments.repository.segment_repository import SegmentRepository

_DISPATCHER = MessageDispatcher()

_MAX_CONCURRENT = 100
_sem = asyncio.Semaphore(_MAX_CONCURRENT)
_executing: set[uuid.UUID] = set()

_COL_RECIPIENT = "contact_value"
_COL_DEBTOR_ID = "debtor_id"
_COL_DOCUMENT = "document_number"


def is_executing(campaign_id: uuid.UUID) -> bool:
    return campaign_id in _executing


def make_automation_service(session: AsyncSession) -> AutomationService:
    return AutomationService(
        campaign_repo=CampaignRepository(session),
        ct_repo=CampaignTimeRepository(session),
        result_repo=CampaignResultRepository(session),
        channel_repo=ChannelRepository(session),
        seg_repo=SegmentRepository(session),
        dml=DmlService(session),
        batch_sender=BatchSender(_DISPATCHER, ContactRepository(session)),
        billing_status_service=BillingStatusService(InvoiceRepository(session)),
    )


class AutomationService:

    def __init__(
        self,
        campaign_repo: CampaignRepository,
        ct_repo: CampaignTimeRepository,
        result_repo: CampaignResultRepository,
        channel_repo: ChannelRepository,
        seg_repo: SegmentRepository,
        dml: DmlService,
        batch_sender: BatchSender,
        billing_status_service: BillingStatusService,
    ) -> None:
        self._campaign_repo = campaign_repo
        self._ct_repo = ct_repo
        self._result_repo = result_repo
        self._channel_repo = channel_repo
        self._seg_repo = seg_repo
        self._dml = dml
        self._batch_sender = batch_sender
        self._billing_status_service = billing_status_service

    async def tick(self) -> int:
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

        processed = 0
        batch_size = 300
        after_id: uuid.UUID | None = None

        while True:
            due = await self._ct_repo.find_due_active(now, batch_size, after_id)
            if not due:
                break

            after_id = due[-1].id

            tasks = [self._guarded_process(ct, now) for ct in due]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for ct, result in zip(due, results):
                if isinstance(result, Exception):
                    logger.error("[automation] error campaña=%s: %s", ct.campaign_id, result)
                elif result:
                    processed += 1

            if len(due) < batch_size:
                break

        return processed

    async def _guarded_process(self, ct: CampaignTimeModel, now: datetime) -> bool:
        if ct.campaign_id in _executing:
            logger.debug("[automation] campaña %s ya en ejecución, omitida", ct.campaign_id)
            return False

        async with _sem:
            _executing.add(ct.campaign_id)
            try:
                return await self._process_due(ct, now)
            finally:
                _executing.discard(ct.campaign_id)

    async def _process_due(self, ct: CampaignTimeModel, now: datetime) -> bool:
        campaign = await self._campaign_repo.get_by_id(ct.campaign_id)
        if campaign is None:
            return False

        if await self._billing_status_service.is_blocked(campaign.organization_id):
            logger.warning(
                "[automation] organización %s bloqueada por facturación, envío de campaña %s omitido",
                campaign.organization_id, campaign.id,
            )
            # No se desactiva ni reprograma: se reintenta en el siguiente tick hasta que se desbloquee.
            return False

        await self._execute_campaign_once(campaign, ct)

        periodicity = campaign.periodicity

        if campaign.is_immediate or periodicity in (None, Periodicity.ONCE):
            await self._ct_repo.deactivate(ct)
            await self._set_campaign_status(campaign, CampaignStatus.COMPLETED)
            logger.info("[automation] campaña %s completada (once/immediate)", campaign.id)
            return True

        if not campaign.time_to_send or not ct.timezone_iana:
            logger.error("[automation] campaña %s sin time_to_send o timezone", campaign.id)
            return True

        try:
            try:
                campaign_tz = ZoneInfo(ct.timezone_iana)
            except (ZoneInfoNotFoundError, KeyError):
                campaign_tz = timezone.utc
            day_in_campaign_tz = now.astimezone(campaign_tz).day

            next_dt = calculate_next_execution(
                periodicity=periodicity.value,
                time_to_send=campaign.time_to_send,
                timezone_iana=ct.timezone_iana,
                days_of_week=ct.days_of_week,
                day_of_month=day_in_campaign_tz,
                from_dt=now,
            )
            await self._ct_repo.reschedule(ct, next_dt)
            logger.info("[automation] campaña %s reprogramada para %s", campaign.id, next_dt)
        except ValueError as exc:
            logger.error("[automation] campaña %s error recalculando: %s", campaign.id, exc)

        return True

    async def _execute_campaign_once(self, campaign: CampaignModel, ct: CampaignTimeModel) -> None:
        if not campaign.segment_id:
            logger.warning("[automation] campaña %s sin segment_id, omitida", campaign.id)
            return

        segment = await self._seg_repo.get_by_id(campaign.segment_id)
        if segment is None:
            logger.error("[automation] segmento %s no encontrado", campaign.segment_id)
            return

        criteria = segment.filter_criteria
        result = await self._dml.execute_query(
            tables=criteria.get("tables", []),
            joins=criteria.get("joins", []),
            limit=criteria.get("limit"),
            query_mode=criteria.get("query_mode", "detail"),
            group_by=criteria.get("group_by", []),
            aggregations=criteria.get("aggregations", []),
            having=criteria.get("having", []),
            order_by=criteria.get("order_by", []),
        )
        if not result.get("success"):
            logger.error("[automation] campaña %s: fallo al ejecutar segmento: %s", campaign.id, result.get("error"))
            return

        rows: list[dict] = json.loads(result.get("data", "[]"))
        if not rows:
            logger.warning("[automation] campaña %s: segmento sin destinatarios", campaign.id)
            return

        logger.info("[automation] campaña %s: %d filas del segmento", campaign.id, len(rows))

        channel_model = await self._channel_repo.get_by_id(campaign.channel_id)
        if channel_model is None:
            logger.error("[automation] campaña %s: canal %s no encontrado", campaign.id, campaign.channel_id)
            return
        snapshot_channel_id = channel_model.id
        snapshot_currency = channel_model.currency
        snapshot_unit_price = channel_model.unit_price

        send_inputs: list[SendInput] = []
        unique_recipients: set[str] = set()

        for row in rows:
            recipient = str(row.get(_COL_RECIPIENT) or "").strip()
            if not recipient or recipient in unique_recipients:
                continue
            unique_recipients.add(recipient)

            raw_debtor_id = row.get(_COL_DEBTOR_ID)
            debtor_id: uuid.UUID | None = None
            if raw_debtor_id:
                try:
                    debtor_id = uuid.UUID(str(raw_debtor_id))
                except ValueError:
                    pass

            send_inputs.append(
                SendInput(
                    recipient=recipient,
                    content=campaign.message,
                    subject=campaign.subject,
                    debtor_id=debtor_id,
                    debtor_document=str(row.get(_COL_DOCUMENT) or "").strip() or None,
                    campaign_id=campaign.id,
                    organization_id=campaign.organization_id,
                    portfolio_id=None,
                    snapshot_channel_id=snapshot_channel_id,
                    snapshot_currency=snapshot_currency,
                    snapshot_unit_price=snapshot_unit_price,
                )
            )

        if not send_inputs:
            logger.warning("[automation] campaña %s: 0 destinatarios válidos", campaign.id)
            return

        stats: BatchStats = await self._batch_sender.process_batch(send_inputs, channel_model.name)

        await self._result_repo.create(
            campaign_id=campaign.id,
            organization_id=campaign.organization_id,
            campaign_time_id=ct.id,
            total_sent=stats.total_sent,
            success_count=stats.success_count,
            failure_count=stats.failure_count,
            unique_customers=stats.unique_customers,
        )

        logger.info(
            "[automation] campaña %s: %d/%d exitosos, %d únicos",
            campaign.id,
            stats.success_count,
            stats.total_sent,
            stats.unique_customers,
        )

    async def _set_campaign_status(self, campaign: CampaignModel, status: CampaignStatus) -> None:
        campaign.status = status
        await self._campaign_repo.update(campaign)
