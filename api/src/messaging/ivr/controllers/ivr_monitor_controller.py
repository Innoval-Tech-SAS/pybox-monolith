import asyncio
import uuid
from typing import Annotated

from fastapi import Query
from sse_starlette.sse import EventSourceResponse

from core.config.api_router import APIRouter
from core.config.logger import logger
from core.security.dependencies import CurrentSession, SSESession
from messaging.ivr.dependencies import IvrMonitorServiceDep
from messaging.ivr.enums.ivr_enums import IvrCallStatus
from messaging.ivr.schemas.ivr_monitor_schemas import (
    IvrCallListResponse,
    IvrCampaignStatsSchema,
    IvrSnapshotSchema,
)
from messaging.ivr.services.ivr_stream_emitter import (
    EVENT_HEARTBEAT,
    campaign_topic,
    ivr_stream,
)

router = APIRouter(prefix="/ivr/monitor", tags=["IVR - Monitor"])

#: Sin tráfico, los proxies inversos cortan las conexiones SSE ociosas. El
#: heartbeat mantiene viva la conexión y le sirve al frontend para distinguir
#: "campaña sin actividad" de "stream caído".
_HEARTBEAT_SECONDS = 25


@router.get(
    "/snapshot",
    response_model=IvrSnapshotSchema,
    summary="Estado actual de las llamadas de una campaña IVR",
)
async def get_snapshot(
    session: CurrentSession,
    service: IvrMonitorServiceDep,
    campaign_id: Annotated[uuid.UUID, Query(alias="campaignId")],
) -> IvrSnapshotSchema:
    return await service.get_snapshot(campaign_id, session)


@router.get(
    "/calls",
    response_model=IvrCallListResponse,
    summary="Listado paginado de llamadas de una campaña IVR",
)
async def list_calls(
    session: CurrentSession,
    service: IvrMonitorServiceDep,
    campaign_id: Annotated[uuid.UUID, Query(alias="campaignId")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=200)] = 50,
    call_status: Annotated[IvrCallStatus | None, Query(alias="status")] = None,
    phone: Annotated[str | None, Query()] = None,
    outcome_key: Annotated[str | None, Query(alias="outcomeKey")] = None,
) -> IvrCallListResponse:
    return await service.list_calls(
        campaign_id, session, page, page_size, call_status, phone, outcome_key
    )


@router.get(
    "/stats",
    response_model=IvrCampaignStatsSchema,
    summary="Contadores de una campaña IVR",
)
async def get_stats(
    session: CurrentSession,
    service: IvrMonitorServiceDep,
    campaign_id: Annotated[uuid.UUID, Query(alias="campaignId")],
) -> IvrCampaignStatsSchema:
    await service.authorize_campaign(campaign_id, session)
    return await service.get_stats(campaign_id)


@router.get(
    "/stream",
    summary="Stream en tiempo real de las llamadas de una campaña IVR (SSE)",
    description=(
        "Conexión Server-Sent Events. Emite `ivr:call-updated`, `ivr:stats-updated`, "
        "`ivr:campaign-status` y `ivr:heartbeat`. La carga inicial se obtiene de "
        "`/ivr/monitor/snapshot`."
    ),
)
async def stream_campaign(
    session: SSESession,
    service: IvrMonitorServiceDep,
    campaign_id: Annotated[uuid.UUID, Query(alias="campaignId")],
) -> EventSourceResponse:
    await service.authorize_campaign(campaign_id, session)

    topic = campaign_topic(campaign_id)
    queue = ivr_stream.subscribe(topic)
    logger.info(
        "[ivr_stream] suscripción abierta | topic=%s usuario=%s suscriptores=%d",
        topic,
        session.user_id,
        ivr_stream.subscriber_count(topic),
    )

    async def generator():
        try:
            while True:
                try:
                    yield await asyncio.wait_for(
                        queue.get(), timeout=_HEARTBEAT_SECONDS
                    )
                except asyncio.TimeoutError:
                    yield {"event": EVENT_HEARTBEAT, "data": "{}"}
        except asyncio.CancelledError:
            pass
        finally:
            ivr_stream.unsubscribe(topic, queue)
            logger.info("[ivr_stream] suscripción cerrada | topic=%s", topic)

    return EventSourceResponse(generator())
