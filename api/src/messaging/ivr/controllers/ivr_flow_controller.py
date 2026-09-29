"""Endpoints de flujos IVR: alta, edición y catálogo."""

import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from messaging.ivr.dependencies import IvrFlowServiceDep
from messaging.ivr.schemas.ivr_flow_schemas import (
    IvrFlowCreateRequest,
    IvrFlowResponse,
    IvrFlowUpdateRequest,
)

router = APIRouter(prefix="/ivr/flows", tags=["IVR - Flujos"])


@router.get(
    "/",
    response_model=list[IvrFlowResponse],
    summary="Listar flujos IVR del portafolio",
)
async def list_flows(
    session: CurrentSession,
    service: IvrFlowServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> list[IvrFlowResponse]:
    flows = await service.list_by_portfolio(portfolio_id, session)
    return [IvrFlowResponse.model_validate(f) for f in flows]


@router.get(
    "/{flow_id}", response_model=IvrFlowResponse, summary="Obtener flujo IVR por ID"
)
async def get_flow(
    flow_id: uuid.UUID,
    session: CurrentSession,
    service: IvrFlowServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> IvrFlowResponse:
    flow = await service.get_by_id(flow_id, portfolio_id, session)
    return IvrFlowResponse.model_validate(flow)


@router.post(
    "/",
    response_model=IvrFlowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear flujo IVR",
)
async def create_flow(
    body: IvrFlowCreateRequest,
    session: CurrentSession,
    service: IvrFlowServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> IvrFlowResponse:
    flow = await service.create(portfolio_id, body, session)
    return IvrFlowResponse.model_validate(flow)


@router.patch(
    "/{flow_id}", response_model=IvrFlowResponse, summary="Actualizar flujo IVR"
)
async def update_flow(
    flow_id: uuid.UUID,
    body: IvrFlowUpdateRequest,
    session: CurrentSession,
    service: IvrFlowServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> IvrFlowResponse:
    flow = await service.update(flow_id, portfolio_id, body, session)
    return IvrFlowResponse.model_validate(flow)


@router.delete(
    "/{flow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar flujo IVR (soft delete)",
)
async def delete_flow(
    flow_id: uuid.UUID,
    session: CurrentSession,
    service: IvrFlowServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> None:
    await service.delete(flow_id, portfolio_id, session)
