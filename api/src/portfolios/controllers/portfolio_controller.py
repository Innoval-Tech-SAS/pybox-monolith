import uuid
from typing import Annotated

from fastapi import HTTPException, Query, UploadFile, status

from config.api_router import APIRouter
from countries.enums.country_enums import Nationality
from onboarding.dependencies import CurrentOrg
from portfolios.dependencies import PortfolioCsvServiceDep, PortfolioServiceDep
from portfolios.models.portfolio_model import PortfolioModel
from portfolios.schemas.portfolio_schemas import PortfolioResponse
from portfolios.services.portfolio_csv_service import CsvProcessResult
from security.dependencies import CurrentSession

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


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


@router.post("/upload-csv", status_code=status.HTTP_200_OK, response_model=None)
async def upload_csv(
    file: UploadFile,
    session: CurrentSession,
    org: CurrentOrg,
    service: PortfolioCsvServiceDep,
    portfolio_name: Annotated[str | None, Query(alias="portfolioName")] = None,
    tenant_id: Annotated[uuid.UUID | None, Query(alias="tenantId")] = None,
    country: Annotated[Nationality | None, Query()] = None,
    country_id: Annotated[Nationality | None, Query(alias="countryId")] = None,
) -> CsvProcessResult:
    selected_org_id = tenant_id or (org.id if org is not None else None)
    if selected_org_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no pertenece a ninguna organización",
        )
    if not session.is_global and str(selected_org_id) not in session.orgs:
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
    if extension != "csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo no permitido. Solo se aceptan archivos .csv",
        )

    file_bytes = await file.read()
    return await service.process_csv(
        file_bytes=file_bytes,
        organization_id=selected_org_id,
        portfolio_name=(portfolio_name or "").strip() or None,
        country=country or country_id,
    )
