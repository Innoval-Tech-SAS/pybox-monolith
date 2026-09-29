import uuid

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.ivr.dependencies import IvrExecutionServiceDep
from messaging.ivr.schemas.ivr_execution_schemas import (
    IvrAllocationRequest,
    IvrExecutionSchema,
    IvrExecutionStatusResponse,
)

router = APIRouter(prefix="/ivr/executions", tags=["IVR - Control de campaña"])


@router.get(
    "/campaign/{campaign_id}",
    response_model=list[IvrExecutionSchema],
    summary="Listar las ejecuciones (bulks) de una campaña IVR",
)
async def list_executions(
    campaign_id: uuid.UUID,
    session: CurrentSession,
    service: IvrExecutionServiceDep,
) -> list[IvrExecutionSchema]:
    executions = await service.list_for_campaign(campaign_id, session)
    return [IvrExecutionSchema.from_model(e) for e in executions]


@router.get(
    "/{bulk_id}/status",
    response_model=IvrExecutionStatusResponse,
    summary="Estado de un bulk (local + snapshot en vivo de Helena)",
)
async def get_status(
    bulk_id: str,
    session: CurrentSession,
    service: IvrExecutionServiceDep,
) -> IvrExecutionStatusResponse:
    execution, helena_status = await service.get_live_status(bulk_id, session)
    return IvrExecutionStatusResponse(
        execution=IvrExecutionSchema.from_model(execution), helena=helena_status
    )


@router.post(
    "/{bulk_id}/pause",
    response_model=IvrExecutionSchema,
    summary="Pausar la marcación de un bulk",
)
async def pause_execution(
    bulk_id: str,
    session: CurrentSession,
    service: IvrExecutionServiceDep,
) -> IvrExecutionSchema:
    execution = await service.pause(bulk_id, session)
    return IvrExecutionSchema.from_model(execution)


@router.post(
    "/{bulk_id}/resume",
    response_model=IvrExecutionSchema,
    summary="Reanudar la marcación de un bulk pausado",
)
async def resume_execution(
    bulk_id: str,
    session: CurrentSession,
    service: IvrExecutionServiceDep,
) -> IvrExecutionSchema:
    execution = await service.resume(bulk_id, session)
    return IvrExecutionSchema.from_model(execution)


@router.post(
    "/{bulk_id}/cancel",
    response_model=IvrExecutionSchema,
    summary="Cancelar un bulk (irreversible)",
)
async def cancel_execution(
    bulk_id: str,
    session: CurrentSession,
    service: IvrExecutionServiceDep,
) -> IvrExecutionSchema:
    execution = await service.cancel(bulk_id, session)
    return IvrExecutionSchema.from_model(execution)


@router.patch(
    "/{bulk_id}/allocation",
    response_model=IvrExecutionSchema,
    summary="Ajustar el ritmo de marcación de un bulk en curso",
)
async def set_allocation(
    bulk_id: str,
    body: IvrAllocationRequest,
    session: CurrentSession,
    service: IvrExecutionServiceDep,
) -> IvrExecutionSchema:
    execution = await service.set_allocation(
        bulk_id, body.calls_per_second, body.max_concurrent, session
    )
    return IvrExecutionSchema.from_model(execution)
