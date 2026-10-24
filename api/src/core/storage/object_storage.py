"""Interfaz abstracta del almacén de objetos, independiente del proveedor."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class ObjectStorageError(RuntimeError):
    """Fallo hablando con el almacén de objetos. El service lo traduce a HTTP."""


@dataclass(frozen=True)
class ObjectMetadata:
    """Lo que el almacén sabe de un objeto ya guardado."""

    size_bytes: int
    content_type: str
    etag: str


class ObjectStorage(ABC):
    """Contrato del almacén de objetos.

    La API es el único cliente: habla con el almacén por la red privada del compose,
    que no está publicada en ningún puerto del host. Los archivos entran y salen por
    acá, siempre después de que un service resolvió quién puede hacerlo.

    Cambiar de backend (SeaweedFS → Garage, Ceph, S3 real) es implementar esta clase;
    los módulos de dominio no la ven, hablan con DocumentService.
    """

    @abstractmethod
    async def startup(self) -> None:
        """Abre el cliente y verifica que el bucket exista. Se llama en el lifespan."""

    @abstractmethod
    async def shutdown(self) -> None: ...

    @abstractmethod
    async def put(self, key: str, data: bytes, content_type: str) -> str:
        """Guarda los bytes y devuelve el ETag que reporta el almacén."""

    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Descarga el objeto completo.

        Devuelve bytes y no un stream a propósito: con el tope de 10 MB por archivo, el
        costo de tenerlo en memoria es menor que el de arrastrar el ciclo de vida de una
        conexión abierta a través de las capas de dominio.
        """

    @abstractmethod
    async def head(self, key: str) -> ObjectMetadata | None:
        """Metadatos del objeto, o None si no existe."""

    @abstractmethod
    async def delete(self, key: str) -> None: ...
