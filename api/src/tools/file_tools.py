import os
import uuid

from fastapi import HTTPException, UploadFile, status

_ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png"}
_ALLOWED_EXTENSIONS = {".pdf", ".png"}
_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
_UPLOADS_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")


async def save_upload_file(file: UploadFile, org_id: str, label: str) -> str:
    _validate_file(file)

    content = await file.read()
    if len(content) > _MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo '{label}' supera el límite de 5 MB",
        )

    ext = os.path.splitext(file.filename or "")[1].lower()
    filename = f"{label}_{uuid.uuid4().hex}{ext}"
    dest_dir = os.path.join(_UPLOADS_ROOT, "organizations", org_id)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, "wb") as f:
        f.write(content)

    return f"organizations/{org_id}/{filename}"


def _validate_file(file: UploadFile) -> None:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se permiten archivos PDF o PNG",
        )
    if file.content_type and file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se permiten archivos PDF o PNG",
        )
