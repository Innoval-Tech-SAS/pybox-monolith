from fastapi import HTTPException, status

from identity.organizations.constants.organization_constants import (
    MAX_DOCUMENT_UPLOAD_SIZE_BYTES,
)


def require_within_size_limit(file_bytes: bytes) -> None:
    if len(file_bytes) > MAX_DOCUMENT_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            "El archivo supera el tamaño máximo permitido (10 MB)",
        )
