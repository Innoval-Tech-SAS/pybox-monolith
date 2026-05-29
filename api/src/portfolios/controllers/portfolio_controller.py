import logging
import uuid
from typing import Annotated

from fastapi import BackgroundTasks, HTTPException, Query, UploadFile, status

from config.api_router import APIRouter
from countries.enums.country_enums import Nationality
from notifications.dependencies import NotificationServiceDep
from onboarding.dependencies import CurrentOrg
from portfolios.dependencies import PortfolioCsvServiceDep, PortfolioServiceDep, PortfolioUserAccessServiceDep
from portfolios.models.portfolio_model import PortfolioModel
from portfolios.models.portfolio_daily_counter_config_model import PortfolioDailyCounterConfigModel
from portfolios.schemas.portfolio_schemas import (
    PortfolioAccessEntry,
    PortfolioAccessReplaceRequest,
    PortfolioDailyCounterConfigResponse,
    PortfolioDailyCounterConfigUpdateRequest,
    PortfolioResponse,
    PortfolioStatsResponse,
    PortfolioUpdateRequest,
)
from security.dependencies import CurrentSession
from security.permissions import PORTFOLIO_UPLOAD_UPDATE
from security.policies import require_portfolio_access
from users.enums.user_enums import UserRole
from users.schemas.user_session_schema import UserSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolios", tags=["Portafolios"])

_uploading_orgs: set[uuid.UUID] = set()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _require_admin(session: UserSession, org_id: str) -> None:
    if session.is_global:
        return
    org_entry = session.orgs.get(org_id)
    if org_entry is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin acceso a esta organización")
    if org_entry.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo administradores pueden realizar esta acción")


def _validate_file(file: UploadFile) -> str:
    filename = file.filename or ""
    if not filename:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El nombre del archivo es inválido")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in {"csv", "xlsx"}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Solo se aceptan archivos .csv o .xlsx")
    return filename


# ------------------------------------------------------------------
# Background task helpers
# ------------------------------------------------------------------

async def _process_and_notify(
    file_bytes: bytes,
    filename: str,
    organization_id: uuid.UUID,
    portfolio_name: str | None,
    country: Nationality | None,
    user_id: int,
    service: PortfolioCsvServiceDep,
    notification_service: NotificationServiceDep,
) -> None:
    logger.info("[portfolio] background task iniciado | org=%s nombre=%s", organization_id, portfolio_name)
    try:
        result = await service.process_csv(
            file_bytes=file_bytes,
            filename=filename,
            organization_id=organization_id,
            portfolio_name=portfolio_name,
            country=country,
        )
        logger.info("[portfolio] process_csv terminado | procesados=%d fallidos=%d", result.processed_rows, result.failed_rows)

        failed_note = f", {result.failed_rows} fallidos" if result.failed_rows > 0 else ""
        notif_type = "error" if result.failed_rows == result.total_rows else (
            "warning" if result.failed_rows > 0 else "success"
        )
        await notification_service.create_notification(
            user_id=user_id,
            title="Portafolio listo",
            body=f"{result.processed_rows} registros procesados{failed_note}.",
            category="portfolio",
            notif_type=notif_type,
            link=f"/my-companies/portfolios?org={organization_id}&portfolioId={result.portfolio_id}",
            details={
                "creditos": result.creditos,
                "titulares": result.titulares,
                "codeudores": result.codeudores,
                "clientes_unicos": result.clientes_unicos,
            },
        )
        logger.info("[portfolio] notificación enviada al usuario %s", user_id)
    except Exception:
        logger.exception("[portfolio] error en background task | org=%s", organization_id)
    finally:
        _uploading_orgs.discard(organization_id)
        logger.info("[portfolio] org liberada del set activo | org=%s", organization_id)


async def _append_and_notify(
    file_bytes: bytes,
    filename: str,
    portfolio_id: uuid.UUID,
    organization_id: uuid.UUID,
    user_id: int,
    service: PortfolioCsvServiceDep,
    notification_service: NotificationServiceDep,
) -> None:
    logger.info("[portfolio-append] background task iniciado | portfolio=%s", portfolio_id)
    try:
        result = await service.append_csv(portfolio_id, file_bytes, filename)
        logger.info("[portfolio-append] terminado | procesados=%d fallidos=%d", result.processed_rows, result.failed_rows)

        failed_note = f", {result.failed_rows} fallidos" if result.failed_rows > 0 else ""
        notif_type = "error" if result.failed_rows == result.total_rows else (
            "warning" if result.failed_rows > 0 else "success"
        )
        await notification_service.create_notification(
            user_id=user_id,
            title="Datos agregados al portafolio",
            body=f"{result.processed_rows} registros procesados{failed_note}.",
            category="portfolio",
            notif_type=notif_type,
            link=f"/my-companies/portfolios?org={organization_id}&portfolioId={portfolio_id}",
            details={
                "creditos": result.creditos,
                "titulares": result.titulares,
                "codeudores": result.codeudores,
                "clientes_unicos": result.clientes_unicos,
            },
        )
    except Exception:
        logger.exception("[portfolio-append] error | portfolio=%s", portfolio_id)
    finally:
        _uploading_orgs.discard(organization_id)


async def _update_and_notify(
    file_bytes: bytes,
    filename: str,
    portfolio_id: uuid.UUID,
    organization_id: uuid.UUID,
    user_id: int,
    service: PortfolioCsvServiceDep,
    notification_service: NotificationServiceDep,
) -> None:
    logger.info("[portfolio-update] background task iniciado | portfolio=%s", portfolio_id)
    try:
        result = await service.update_csv(portfolio_id, file_bytes, filename)
        logger.info("[portfolio-update] terminado | procesados=%d fallidos=%d", result.processed_rows, result.failed_rows)

        failed_note = f", {result.failed_rows} fallidos" if result.failed_rows > 0 else ""
        notif_type = "error" if result.failed_rows == result.total_rows else (
            "warning" if result.failed_rows > 0 else "success"
        )
        await notification_service.create_notification(
            user_id=user_id,
            title="Portafolio actualizado",
            body=f"{result.processed_rows} registros procesados{failed_note}.",
            category="portfolio",
            notif_type=notif_type,
            link=f"/my-companies/portfolios?org={organization_id}&portfolioId={portfolio_id}",
            details={
                "creditos": result.creditos,
                "titulares": result.titulares,
                "codeudores": result.codeudores,
                "clientes_unicos": result.clientes_unicos,
            },
        )
    except Exception:
        logger.exception("[portfolio-update] error | portfolio=%s", portfolio_id)
    finally:
        _uploading_orgs.discard(organization_id)


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

    filename = _validate_file(file)

    if selected_org_id in _uploading_orgs:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Ya estás cargando un portfolio, intenta más tarde.")

    file_bytes = await file.read()
    _uploading_orgs.add(selected_org_id)
    logger.info("[portfolio] archivo leído | tamaño=%d bytes | org=%s", len(file_bytes), selected_org_id)

    background_tasks.add_task(
        _process_and_notify,
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

    filename = _validate_file(file)

    if portfolio.organization_id in _uploading_orgs:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Ya hay una carga activa para esta organización.")

    file_bytes = await file.read()
    _uploading_orgs.add(portfolio.organization_id)

    background_tasks.add_task(
        _append_and_notify,
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

    _require_admin(session, org_id_str)

    if not session.is_global:
        org_entry = session.orgs.get(org_id_str)
        if org_entry and PORTFOLIO_UPLOAD_UPDATE not in org_entry.permissions:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin permiso para actualizar el portafolio")

    filename = _validate_file(file)

    if portfolio.organization_id in _uploading_orgs:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Ya hay una carga activa para esta organización.")

    file_bytes = await file.read()
    _uploading_orgs.add(portfolio.organization_id)

    background_tasks.add_task(
        _update_and_notify,
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
    _require_admin(session, str(portfolio.organization_id))
    return await service.update_portfolio(portfolio_id, data)


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar portafolio")
async def delete_portfolio(
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    service: PortfolioServiceDep,
) -> None:
    portfolio = await service.get_by_id(portfolio_id)
    _require_admin(session, str(portfolio.organization_id))
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
    _require_admin(session, str(portfolio.organization_id))
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
    _require_admin(session, str(portfolio.organization_id))
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
    _require_admin(session, str(portfolio.organization_id))
    return await service.update_daily_counter_config(portfolio_id, data, session.user_id)
