import logging
import uuid
from typing import Annotated

from fastapi import BackgroundTasks, HTTPException, Query, UploadFile, status

from config.api_router import APIRouter
from countries.enums.country_enums import Nationality
from notifications.dependencies import NotificationServiceDep
from onboarding.dependencies import CurrentOrg
from portfolios.dependencies import PortfolioCsvServiceDep, PortfolioServiceDep
from portfolios.models.portfolio_model import PortfolioModel
from portfolios.schemas.portfolio_schemas import PortfolioResponse, PortfolioStatsResponse
from portfolios.services.portfolio_csv_service import CsvProcessResult
from security.dependencies import CurrentSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

# Orgs con carga activa en este proceso. Protege contra uploads concurrentes por org.
_uploading_orgs: set[uuid.UUID] = set()


@router.get("/", response_model=list[PortfolioResponse])
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


async def _process_and_notify(
    file_bytes: bytes,
    filename: str,
    organization_id: uuid.UUID,
    portfolio_name: str | None,
    country: Nationality | None,
    user_id: uuid.UUID,
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


@router.get("/{portfolio_id}/stats", response_model=PortfolioStatsResponse)
async def get_portfolio_stats(
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    service: PortfolioServiceDep,
) -> PortfolioStatsResponse:
    return await service.get_stats(portfolio_id)


@router.post("/upload-csv", status_code=status.HTTP_202_ACCEPTED, response_model=None)
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
        logger.warning("[portfolio] sin org_id — usuario sin organización")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no pertenece a ninguna organización",
        )
    if not session.is_global and str(selected_org_id) not in session.orgs:
        logger.warning("[portfolio] acceso denegado | org=%s session.orgs=%s", selected_org_id, session.orgs)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin acceso a esta organización",
        )

    filename = file.filename or ""
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del archivo es inválido",
        )

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in {"csv", "xlsx"}:
        logger.warning("[portfolio] archivo inválido: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo no permitido. Solo se aceptan archivos .csv o .xlsx",
        )

    if selected_org_id in _uploading_orgs:
        logger.warning("[portfolio] 429 — ya hay carga activa | org=%s", selected_org_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Ya estás cargando un portfolio, intenta más tarde.",
        )

    file_bytes = await file.read()
    logger.info("[portfolio] archivo leído | tamaño=%d bytes | org=%s", len(file_bytes), selected_org_id)

    _uploading_orgs.add(selected_org_id)
    logger.info("[portfolio] org marcada como activa | org=%s | activas=%d", selected_org_id, len(_uploading_orgs))

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

    logger.info("[portfolio] tarea en background programada | respondiendo 202 inmediatamente")
    return None
