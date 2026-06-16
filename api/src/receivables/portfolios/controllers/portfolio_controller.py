import uuid
from typing import Annotated

from fastapi import BackgroundTasks, HTTPException, Query, UploadFile, status

from core.config.api_router import APIRouter
from core.config.logger import logger
from platform.countries.enums.country_enums import Nationality
from platform.notifications.dependencies import NotificationServiceDep
from identity.onboarding.dependencies import CurrentOrg
from receivables.portfolios.background_tasks import append_and_notify, process_and_notify, update_and_notify, uploading_orgs
from receivables.portfolios.dependencies import PortfolioCsvServiceDep, PortfolioServiceDep, PortfolioUserAccessServiceDep
from receivables.portfolios.models.portfolio_model import PortfolioModel
from receivables.portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel
from receivables.portfolios.schemas.portfolio_schemas import (
    PortfolioAccessEntry,
    PortfolioAccessReplaceRequest,
    PortfolioDailyCounterConfigResponse,
    PortfolioDailyCounterConfigSyncRequest,
    PortfolioDailyCounterConfigUpdateRequest,
    PortfolioResponse,
    PortfolioStatsResponse,
    PortfolioUpdateRequest,
)
from receivables.portfolios.utils.file_utils import validate_portfolio_file
from core.security.dependencies import CurrentSession
from core.security.permissions import PORTFOLIO_UPLOAD_UPDATE
from core.security.policies import require_org_admin, require_portfolio_access

router = APIRouter(prefix="/portfolios", tags=["Portafolios"])


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@router.get("/", response_model=list[PortfolioResponse], summary="Listar portafolios accesibles")
async def list_portfolios(
    session: CurrentSession,
    service: PortfolioServiceDep,
    organization_id: Annotated[uuid.UUID | None, Query(alias="organizationId")] = None,
    tenant_id: Annotated[uuid.UUID | None, Query(alias="tenantId")] = None,
    is_active: Annotated[bool | None, Query(alias="isActive")] = None,
) -> list[PortfolioModel]:
    selected_org_id = organization_id or tenant_id
    if (
        organization_id is not None
        and tenant_id is not None
        and organization_id != tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="organizationId y tenantId no coinciden",
        )
    return await service.list_accessible_portfolios(session, selected_org_id, is_active)


@router.post("/upload-csv", status_code=status.HTTP_202_ACCEPTED, response_model=None, summary="Crear portafolio desde CSV/XLSX")
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    session: CurrentSession,
    org: CurrentOrg,
    service: PortfolioCsvServiceDep,
    notification_service: NotificationServiceDep,
    portfolio_name: Annotated[str | None, Query(alias="portfolioName")] = None,
    tenant_id: Annotated[uuid.UUID | None, Query(alias="tenantId")] = None,
    country: Annotated[Nationality | None, Query()] = None,
    country_id: Annotated[Nationality | None, Query(alias="countryId")] = None,
) -> None:
    logger.info("[portfolio] upload-csv recibido | tenant_id=%s portfolio_name=%s", tenant_id, portfolio_name)

    selected_org_id = tenant_id or (org.id if org is not None else None)
    if selected_org_id is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "El usuario no pertenece a ninguna organización")
    if not session.is_global and str(selected_org_id) not in session.orgs:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")

    filename = validate_portfolio_file(file)

    if selected_org_id in uploading_orgs:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Ya estás cargando un portfolio, intenta más tarde.")

    file_bytes = await file.read()
    uploading_orgs.add(selected_org_id)
    logger.info("[portfolio] archivo leído | tamaño=%d bytes | org=%s", len(file_bytes), selected_org_id)

    background_tasks.add_task(
        process_and_notify,
        file_bytes=file_bytes,
        filename=filename,
        organization_id=selected_org_id,
        portfolio_name=(portfolio_name or "").strip() or None,
        country=country or country_id,
        user_id=session.user_id,
        service=service,
        notification_service=notification_service,
    )
    return None


@router.post("/upload-csv/append", status_code=status.HTTP_202_ACCEPTED, response_model=None, summary="Agregar registros al portafolio desde CSV/XLSX")
async def upload_csv_append(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    session: CurrentSession,
    service: PortfolioCsvServiceDep,
    portfolio_service: PortfolioServiceDep,
    notification_service: NotificationServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> None:
    portfolio = await portfolio_service.get_by_id(portfolio_id)
    org_id_str = str(portfolio.organization_id)

    if not session.is_global:
        org_entry = session.orgs.get(org_id_str)
        if org_entry is None:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
        if PORTFOLIO_UPLOAD_UPDATE not in org_entry.permissions:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin permiso para agregar datos al portafolio")

    filename = validate_portfolio_file(file)

    if portfolio.organization_id in uploading_orgs:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Ya hay una carga activa para esta organización.")

    file_bytes = await file.read()
    uploading_orgs.add(portfolio.organization_id)

    background_tasks.add_task(
        append_and_notify,
        file_bytes=file_bytes,
        filename=filename,
        portfolio_id=portfolio_id,
        organization_id=portfolio.organization_id,
        user_id=session.user_id,
        service=service,
        notification_service=notification_service,
    )
    return None


@router.post("/upload-csv/update", status_code=status.HTTP_202_ACCEPTED, response_model=None, summary="Actualizar portafolio existente desde CSV/XLSX")
async def upload_csv_update(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    session: CurrentSession,
    service: PortfolioCsvServiceDep,
    portfolio_service: PortfolioServiceDep,
    notification_service: NotificationServiceDep,
    portfolio_id: Annotated[uuid.UUID, Query(alias="portfolioId")],
) -> None:
    portfolio = await portfolio_service.get_by_id(portfolio_id)
    org_id_str = str(portfolio.organization_id)

    require_org_admin(session, org_id_str)

    if not session.is_global:
        org_entry = session.orgs.get(org_id_str)
        if org_entry and PORTFOLIO_UPLOAD_UPDATE not in org_entry.permissions:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin permiso para actualizar el portafolio")

    filename = validate_portfolio_file(file)

    if portfolio.organization_id in uploading_orgs:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Ya hay una carga activa para esta organización.")

    file_bytes = await file.read()
    uploading_orgs.add(portfolio.organization_id)

    background_tasks.add_task(
        update_and_notify,
        file_bytes=file_bytes,
        filename=filename,
        portfolio_id=portfolio_id,
        organization_id=portfolio.organization_id,
        user_id=session.user_id,
        service=service,
        notification_service=notification_service,
    )
    return None


@router.get("/{portfolio_id}", response_model=PortfolioResponse, summary="Obtener portafolio por ID")
async def get_portfolio(
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    service: PortfolioServiceDep,
    access_service: PortfolioUserAccessServiceDep,
) -> PortfolioModel:
    portfolio = await service.get_by_id(portfolio_id)
    await require_portfolio_access(
        session,
        str(portfolio.organization_id),
        portfolio_id,
        access_service.check_access,
    )
    return portfolio


@router.patch("/{portfolio_id}", response_model=PortfolioResponse, summary="Actualizar portafolio")
async def update_portfolio(
    portfolio_id: uuid.UUID,
    data: PortfolioUpdateRequest,
    session: CurrentSession,
    service: PortfolioServiceDep,
) -> PortfolioModel:
    portfolio = await service.get_by_id(portfolio_id)
    require_org_admin(session, str(portfolio.organization_id))
    return await service.update_portfolio(portfolio_id, data)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar portafolio")
async def delete_portfolio(
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    service: PortfolioServiceDep,
) -> None:
    portfolio = await service.get_by_id(portfolio_id)
    require_org_admin(session, str(portfolio.organization_id))
    await service.delete_portfolio(portfolio_id)


@router.get("/{portfolio_id}/stats", response_model=PortfolioStatsResponse, summary="Obtener estadísticas del portafolio")
async def get_portfolio_stats(
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    service: PortfolioServiceDep,
) -> PortfolioStatsResponse:
    return await service.get_stats(portfolio_id)


@router.get("/{portfolio_id}/access", response_model=list[PortfolioAccessEntry], summary="Listar usuarios con acceso al portafolio")
async def list_portfolio_access(
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    service: PortfolioServiceDep,
    access_service: PortfolioUserAccessServiceDep,
) -> list:
    portfolio = await service.get_by_id(portfolio_id)
    require_org_admin(session, str(portfolio.organization_id))
    return await access_service.list_portfolio_access(portfolio_id)


@router.put("/{portfolio_id}/access", response_model=list[PortfolioAccessEntry], summary="Reemplazar lista de acceso al portafolio")
async def replace_portfolio_access(
    portfolio_id: uuid.UUID,
    body: PortfolioAccessReplaceRequest,
    session: CurrentSession,
    service: PortfolioServiceDep,
    access_service: PortfolioUserAccessServiceDep,
) -> list:
    portfolio = await service.get_by_id(portfolio_id)
    require_org_admin(session, str(portfolio.organization_id))
    return await access_service.replace_access(
        portfolio_id,
        portfolio.organization_id,
        body.user_ids,
        session.user_id,
    )


@router.get("/{portfolio_id}/daily-counter-config", response_model=PortfolioDailyCounterConfigResponse | None, summary="Obtener configuración del contador diario")
async def get_daily_counter_config(
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    service: PortfolioServiceDep,
    access_service: PortfolioUserAccessServiceDep,
) -> PortfolioDailyCounterConfigModel | None:
    portfolio = await service.get_by_id(portfolio_id)
    await require_portfolio_access(
        session,
        str(portfolio.organization_id),
        portfolio_id,
        access_service.check_access,
    )
    return await service.get_daily_counter_config(portfolio_id)


@router.patch("/{portfolio_id}/daily-counter-config", response_model=PortfolioDailyCounterConfigResponse, summary="Actualizar configuración del contador diario")
async def update_daily_counter_config(
    portfolio_id: uuid.UUID,
    data: PortfolioDailyCounterConfigUpdateRequest,
    session: CurrentSession,
    service: PortfolioServiceDep,
) -> PortfolioDailyCounterConfigModel:
    portfolio = await service.get_by_id(portfolio_id)
    require_org_admin(session, str(portfolio.organization_id))
    return await service.update_daily_counter_config(portfolio_id, data, session.user_id)


@router.post("/{portfolio_id}/daily-counter-config/sync", response_model=PortfolioDailyCounterConfigResponse, summary="Sincronizar manualmente el contador diario")
async def sync_daily_counter_config(
    portfolio_id: uuid.UUID,
    data: PortfolioDailyCounterConfigSyncRequest,
    session: CurrentSession,
    service: PortfolioServiceDep,
) -> PortfolioDailyCounterConfigModel:
    portfolio = await service.get_by_id(portfolio_id)
    require_org_admin(session, str(portfolio.organization_id))
    return await service.sync_daily_counter_config(portfolio_id, data, session.user_id)
