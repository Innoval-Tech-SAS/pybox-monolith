from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile, status
from config.api_router import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import TokenPayload
from contacts.services.contact_services import ContactServices
from database.database import get_main_session

router = APIRouter(prefix="/contacts", tags=["contacts"])

MainSession = Annotated[AsyncSession, Depends(get_main_session)]

_ALLOWED_EXTENSIONS = {"csv", "xlsx"}


@router.post("/upload-file", status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile,
    _: TokenPayload,
    session: MainSession,
) -> dict:
    filename = file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del archivo es inválido",
        )

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo no permitido. Solo se aceptan archivos .csv o .xlsx",
        )

    file_bytes = await file.read()
    service = ContactServices(session)
    resumen = await service.process_file(file_bytes, extension)

    return {
        "message": f"Archivo '{filename}' recibido exitosamente!",
        "resumen": resumen,
    }
