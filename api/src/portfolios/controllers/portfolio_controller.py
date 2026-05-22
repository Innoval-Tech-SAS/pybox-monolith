from typing import Annotated

from fastapi import Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.api_router import APIRouter
from countries.enums.country_enums import Nationality
from database.database import get_main_session
from onboarding.dependencies import CurrentOrg
from portfolios.services.portfolio_csv_service import CsvProcessResult, PortfolioCsvService

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

MainSession = Annotated[AsyncSession, Depends(get_main_session)]


@router.post("/upload-csv", status_code=status.HTTP_200_OK, response_model=None)
async def upload_csv(
    file: UploadFile,
    org: CurrentOrg,
    session: MainSession,
    portfolio_name: Annotated[str | None, Query()] = None,
    country: Annotated[Nationality | None, Query()] = None,
) -> CsvProcessResult:
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no pertenece a ninguna organización",
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
    service = PortfolioCsvService(session)
    return await service.process_csv(
        file_bytes=file_bytes,
        organization_id=org.id,
        portfolio_name=portfolio_name,
        country=country,
    )
