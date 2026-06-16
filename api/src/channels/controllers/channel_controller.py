from fastapi import status

from channels.dependencies import ChannelServiceDep
from channels.schemas.channel_schemas import (
    ChannelCreateRequest,
    ChannelResponse,
    ChannelUpdateRequest,
)
from config.api_router import APIRouter
from security.dependencies import CurrentSession
from security.policies import require_global, require_global_admin

router = APIRouter(prefix="/channels", tags=["Canales"])


@router.get("/", response_model=list[ChannelResponse], summary="Listar canales disponibles")
async def list_channels(
    session: CurrentSession,
    service: ChannelServiceDep,
) -> list[ChannelResponse]:
    require_global(session)
    channels = await service.list_all()
    return [ChannelResponse.model_validate(c) for c in channels]


@router.get("/{channel_id}", response_model=ChannelResponse, summary="Obtener canal por ID")
async def get_channel(
    channel_id: int,
    session: CurrentSession,
    service: ChannelServiceDep,
) -> ChannelResponse:
    require_global(session)
    channel = await service.get_by_id(channel_id)
    return ChannelResponse.model_validate(channel)


@router.post(
    "/",
    response_model=ChannelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear canal",
)
async def create_channel(
    body: ChannelCreateRequest,
    session: CurrentSession,
    service: ChannelServiceDep,
) -> ChannelResponse:
    require_global_admin(session)
    channel = await service.create(body)
    return ChannelResponse.model_validate(channel)


@router.patch("/{channel_id}", response_model=ChannelResponse, summary="Actualizar canal")
async def update_channel(
    channel_id: int,
    body: ChannelUpdateRequest,
    session: CurrentSession,
    service: ChannelServiceDep,
) -> ChannelResponse:
    require_global_admin(session)
    channel = await service.update(channel_id, body)
    return ChannelResponse.model_validate(channel)


@router.delete(
    "/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar canal",
)
async def delete_channel(
    channel_id: int,
    session: CurrentSession,
    service: ChannelServiceDep,
) -> None:
    require_global_admin(session)
    await service.delete(channel_id)
