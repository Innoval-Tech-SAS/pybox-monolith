from fastapi import HTTPException, UploadFile, status
from config.api_router import APIRouter

from auth.dependencies import TokenPayload
from contacts.dependencies import ContactServiceDep

router = APIRouter(prefix="/contacts", tags=["Contactos"])

_ALLOWED_EXTENSIONS = {"csv", "xlsx"}


@router.post(
    "/upload-file",
    status_code=status.HTTP_200_OK,
    summary="Cargar archivo de contactos",
    description="Procesa un archivo CSV o XLSX con contactos y retorna un resumen del resultado.",
)
async def upload_file(
    file: UploadFile,
    _: TokenPayload,
    service: ContactServiceDep,
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
    resumen = await service.process_file(file_bytes, extension)

    return {
        "message": f"Archivo '{filename}' recibido exitosamente!",
        "resumen": resumen,
    }
