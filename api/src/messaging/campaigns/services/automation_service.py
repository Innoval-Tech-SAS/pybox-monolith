"""
Ejecuta campañas vencidas, persiste resultados y reprograma la siguiente ejecución.

Equivalente Python del AutomationService de pybox, adaptado para monolito:
- Sin gRPC: segmentos consultados localmente via DmlService
- Sin event streaming: logging directo
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app_platform.schema_manager.services.dml_service import DmlService
from core.config.logger import logger
from messaging.campaigns.enums.campaign_enums import CampaignStatus, Periodicity
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.repositories.campaign_repositories import CampaignRepository
from messaging.campaigns.repositories.campaign_result_repository import CampaignResultRepository
from messaging.campaigns.repositories.campaign_time_repository import CampaignTimeRepository
from messaging.campaigns.services.batch_sender import BatchStats, SendInput, process_batch
from messaging.campaigns.utils.calculate_next import calculate_next_execution
from messaging.channels.enums.channel_enums import ChannelName
from messaging.channels.repositories.channel_repository import ChannelRepository
from messaging.gateway import DeliveryGateway
from receivables.segments.repository.segment_repository import SegmentRepository

_GATEWAY = DeliveryGateway()

# Columnas que el segmento DEBE exponer para campañas de mensajería
_COL_RECIPIENT = "contact_value"
_COL_DEBTOR_ID = "debtor_id"
_COL_DOCUMENT = "document_number"


async def tick_now(session: AsyncSession) -> int:
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    ct_repo = CampaignTimeRepository(session)

    processed = 0
    batch_size = 300
    after_id: uuid.UUID | None = None

    while True:
        due = await ct_repo.find_due_active(now, batch_size, after_id)
        if not due:
            break

        after_id = due[-1].id

        tasks = [_process_due(ct, now, session) for ct in due]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for ct, result in zip(due, results):
            if isinstance(result, Exception):
                logger.error("[automation] error campaña=%s: %s", ct.campaign_id, result)
            elif result:
                processed += 1

        if len(due) < batch_size:
            break

    return processed


async def _process_due(ct: CampaignTimeModel, now: datetime, session: AsyncSession) -> bool:
    campaign_repo = CampaignRepository(session)
    campaign = await campaign_repo.get_by_id(ct.campaign_id)
    if campaign is None:
        return False

    await _execute_campaign_once(campaign, ct, session)

    ct_repo = CampaignTimeRepository(session)
    periodicity = campaign.periodicity

    if campaign.is_immediate or periodicity in (None, Periodicity.ONCE):
        await ct_repo.deactivate(ct)
        await _set_campaign_status(campaign, campaign_repo, CampaignStatus.COMPLETED)
        logger.info("[automation] campaña %s completada (once/immediate)", campaign.id)
        return True

    if not campaign.time_to_send or not ct.timezone_iana:
        logger.error("[automation] campaña %s sin time_to_send o timezone", campaign.id)
        return True

    try:
        next_dt = calculate_next_execution(
            periodicity=periodicity.value,
            time_to_send=campaign.time_to_send,
            timezone_iana=ct.timezone_iana,
            days_of_week=ct.days_of_week,
            day_of_month=now.astimezone().day,
            from_dt=now,
        )
        await ct_repo.reschedule(ct, next_dt)
        logger.info("[automation] campaña %s reprogramada para %s", campaign.id, next_dt)
    except ValueError as exc:
        logger.error("[automation] campaña %s error recalculando: %s", campaign.id, exc)

    return True


async def _execute_campaign_once(
    campaign: CampaignModel,
    ct: CampaignTimeModel,
    session: AsyncSession,
) -> None:
    if not campaign.segment_id:
        logger.warning("[automation] campaña %s sin segment_id, omitida", campaign.id)
        return

    # 1. Obtener segmento
    seg_repo = SegmentRepository(session)
    segment = await seg_repo.get_by_id(campaign.segment_id)
    if segment is None:
        logger.error("[automation] segmento %s no encontrado", campaign.segment_id)
        return

    # 2. Ejecutar filtro del segmento via DmlService
    dml = DmlService(session)
    criteria = segment.filter_criteria
    result = await dml.execute_query(
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

    # 3. Obtener snapshot del canal
    snapshot_channel_id: uuid.UUID | None = None
    snapshot_currency: str | None = None
    snapshot_unit_price = None
    ch_repo = ChannelRepository(session)
    try:
        channel_enum = ChannelName(campaign.channel.upper())
    except ValueError:
        channel_enum = None
    channel_model = await ch_repo.get_by_name(channel_enum) if channel_enum else None
    if channel_model:
        snapshot_channel_id = channel_model.id if isinstance(channel_model.id, uuid.UUID) else None
        snapshot_currency = channel_model.currency
        snapshot_unit_price = channel_model.unit_price

    # 4. Construir SendInput por destinatario
    send_inputs: list[SendInput] = []
    unique_recipients: set[str] = set()

    for row in rows:
        recipient = str(row.get(_COL_RECIPIENT) or "").strip()
        if not recipient:
            continue
        if recipient in unique_recipients:
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

    # 5. Procesar lotes y persistir contactos
    stats: BatchStats = await process_batch(send_inputs, campaign.channel, session, _GATEWAY)

    # 6. Guardar resultado
    result_repo = CampaignResultRepository(session)
    await result_repo.create(
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


async def _set_campaign_status(
    campaign: CampaignModel,
    repo: CampaignRepository,
    status: CampaignStatus,
) -> None:
    campaign.status = status
    await repo.update(campaign)
