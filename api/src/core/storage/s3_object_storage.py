"""Implementación de ObjectStorage sobre la API S3 (SeaweedFS en este proyecto)."""

from contextlib import AsyncExitStack
from typing import Any, Optional

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError

from core.config.logger import logger
from core.config.storage_config import StorageConfig
from core.storage.object_storage import (
    ObjectMetadata,
    ObjectStorage,
    ObjectStorageError,
)


class S3ObjectStorage(ObjectStorage):
    """Implementación sobre la API S3. Probada contra SeaweedFS.

    El cliente se abre una vez en el arranque y se reutiliza: aiobotocore carga el
    modelo del servicio S3 al crearlo, y hacerlo por request agregaría latencia a cada
    descarga.
    """

    def __init__(self, config: Optional[StorageConfig] = None) -> None:
        self._config = config or StorageConfig()
        self._session = aioboto3.Session()
        self._stack: Optional[AsyncExitStack] = None
        self._client: Any = None

    @property
    def bucket(self) -> str:
        return self._config.bucket

    # ── Ciclo de vida ────────────────────────────────────────────────────────

    async def startup(self) -> None:
        stack = AsyncExitStack()
        self._client = await stack.enter_async_context(
            self._session.client(
                "s3",
                endpoint_url=self._config.endpoint,
                aws_access_key_id=self._config.access_key,
                aws_secret_access_key=self._config.secret_key,
                region_name=self._config.region,
                # path-style: SeaweedFS no resuelve buckets como subdominio.
                config=Config(
                    s3={"addressing_style": "path"}, signature_version="s3v4"
                ),
            )
        )
        self._stack = stack
        await self._ensure_bucket()

    async def shutdown(self) -> None:
        if self._stack is not None:
            await self._stack.aclose()
            self._stack = None
            self._client = None

    async def _ensure_bucket(self) -> None:
        client = self._require()
        try:
            await client.head_bucket(Bucket=self.bucket)
            logger.info("[storage] bucket listo | bucket=%s", self.bucket)
            return
        except ClientError as error:
            if self._status(error) not in (403, 404):
                raise ObjectStorageError(
                    f"No se pudo verificar el bucket: {error}"
                ) from error

        try:
            await client.create_bucket(Bucket=self.bucket)
            logger.info("[storage] bucket creado | bucket=%s", self.bucket)
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") in (
                "BucketAlreadyOwnedByYou",
                "BucketAlreadyExists",
            ):
                return
            raise ObjectStorageError(f"No se pudo crear el bucket: {error}") from error

    # ── Operaciones ──────────────────────────────────────────────────────────

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        client = self._require()
        try:
            response = await client.put_object(
                Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
            )
        except ClientError as error:
            raise ObjectStorageError(
                f"No se pudo guardar el objeto '{key}': {error}"
            ) from error
        return str(response.get("ETag", "")).strip('"')

    async def get(self, key: str) -> bytes:
        client = self._require()
        try:
            response = await client.get_object(Bucket=self.bucket, Key=key)
            async with response["Body"] as body:
                return await body.read()
        except ClientError as error:
            if self._status(error) == 404:
                raise ObjectStorageError(f"El objeto '{key}' no existe") from error
            raise ObjectStorageError(
                f"No se pudo leer el objeto '{key}': {error}"
            ) from error

    async def head(self, key: str) -> ObjectMetadata | None:
        client = self._require()
        try:
            response = await client.head_object(Bucket=self.bucket, Key=key)
        except ClientError as error:
            if self._status(error) in (403, 404):
                return None
            raise ObjectStorageError(
                f"No se pudo consultar el objeto '{key}': {error}"
            ) from error

        return ObjectMetadata(
            size_bytes=int(response.get("ContentLength", 0)),
            content_type=response.get("ContentType", "application/octet-stream"),
            etag=str(response.get("ETag", "")).strip('"'),
        )

    async def delete(self, key: str) -> None:
        client = self._require()
        try:
            await client.delete_object(Bucket=self.bucket, Key=key)
        except ClientError as error:
            raise ObjectStorageError(
                f"No se pudo borrar el objeto '{key}': {error}"
            ) from error

    # ── Internos ─────────────────────────────────────────────────────────────

    def _require(self) -> Any:
        if self._client is None:
            raise ObjectStorageError("El almacén de objetos no está inicializado")
        return self._client

    @staticmethod
    def _status(error: ClientError) -> int:
        return int(error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0))


# Instancia única. El tipo declarado es la interfaz, no la implementación: cambiar de
# backend es cambiar esta línea.
object_storage: ObjectStorage = S3ObjectStorage()
