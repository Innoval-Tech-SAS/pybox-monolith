"""Lectura de un archivo subido con corte temprano al superar el tamaño máximo."""

from fastapi import HTTPException, UploadFile, status


async def read_within_limit(upload: UploadFile, max_bytes: int) -> bytes:
    """Lee un archivo subido en chunks y corta apenas se supera el máximo, en vez de
    bufferear todo el contenido en memoria antes de poder rechazarlo."""
    if upload.size is not None and upload.size > max_bytes:
        limit_mb = max_bytes // (1024 * 1024)
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"El archivo excede el tamaño máximo de {limit_mb} MB",
        )
    chunks = bytearray()
    while True:
        chunk = await upload.read(1024 * 1024)
        if not chunk:
            break
        chunks.extend(chunk)
        if len(chunks) > max_bytes:
            limit_mb = max_bytes // (1024 * 1024)
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"El archivo excede el tamaño máximo de {limit_mb} MB",
            )
    return bytes(chunks)
