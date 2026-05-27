import os
import uuid

from fastapi import HTTPException, UploadFile, status

from config.paths import UPLOADS_ROOT
from config.logger import logger

_ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png"}
_ALLOWED_EXTENSIONS = {".pdf", ".png"}
_ALLOWED_PROFILE_PHOTO_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
_ALLOWED_PROFILE_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


async def save_upload_file(file: UploadFile, org_id: str, label: str) -> str:
    _validate_file(file)

    content = await file.read()
    if len(content) > _MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo '{label}' supera el límite de 5 MB",
        )

    ext = os.path.splitext(file.filename or "")[1].lower()
    filename = f"documento_{label}{ext}"
    dest_dir = os.path.join(UPLOADS_ROOT, "organizations", org_id)
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


async def save_profile_photo_file(file: UploadFile, user_id: int) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    content_type_ext = _ALLOWED_PROFILE_PHOTO_CONTENT_TYPES.get(file.content_type or "")
    logger.debug(
        "[profile-photo] save start user_id=%s filename=%s content_type=%s ext=%s",
        user_id,
        file.filename,
        file.content_type,
        ext,
    )

    if ext not in _ALLOWED_PROFILE_PHOTO_EXTENSIONS and content_type_ext is None:
        logger.debug("[profile-photo] save rejected user_id=%s reason=unsupported_type", user_id)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se permiten imágenes JPG, PNG o WebP",
        )

    content = await file.read()
    if len(content) > _MAX_SIZE_BYTES:
        logger.debug(
            "[profile-photo] save rejected user_id=%s reason=size size=%s",
            user_id,
            len(content),
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="La foto de perfil supera el límite de 5 MB",
        )

    normalized_ext = ".jpg" if ext == ".jpeg" else ext
    if normalized_ext not in _ALLOWED_PROFILE_PHOTO_EXTENSIONS:
        normalized_ext = content_type_ext or ".png"

    dest_dir = os.path.join(UPLOADS_ROOT, "users", str(user_id))
    os.makedirs(dest_dir, exist_ok=True)

    filename = f"foto_perfil_{uuid.uuid4().hex}{normalized_ext}"
    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, "wb") as f:
        f.write(content)

    public_url = f"/files/users/{user_id}/{filename}"
    logger.debug(
        "[profile-photo] save done user_id=%s public_url=%s size=%s",
        user_id,
        public_url,
        len(content),
    )
    return public_url


def delete_public_upload(public_url: str | None) -> None:
    if not public_url or not public_url.startswith("/files/"):
        logger.debug("[profile-photo] delete skipped public_url=%s", public_url)
        return

    relative_path = public_url.removeprefix("/files/").lstrip("/\\")
    root = os.path.abspath(UPLOADS_ROOT)
    target = os.path.abspath(os.path.join(root, relative_path))
    root_prefix = root if root.endswith(os.sep) else f"{root}{os.sep}"

    if not target.startswith(root_prefix) or not os.path.isfile(target):
        logger.debug("[profile-photo] delete skipped public_url=%s target=%s", public_url, target)
        return

    os.remove(target)
    logger.debug("[profile-photo] delete done public_url=%s target=%s", public_url, target)
