"""Validación del nombre/extensión de un archivo de carga de portafolio."""

from fastapi import HTTPException, UploadFile, status


def validate_portfolio_file(file: UploadFile) -> str:
    filename = file.filename or ""
    if not filename:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "El nombre del archivo es inválido"
        )
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in {"csv", "xlsx"}:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Solo se aceptan archivos .csv o .xlsx"
        )
    return filename
