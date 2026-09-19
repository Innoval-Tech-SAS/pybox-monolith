from dataclasses import dataclass, field

from core.tools.config_tools import get_or_default, get_or_throw

DEFAULT_STORAGE_BUCKET = "documentos"
# SeaweedFS ignora la región, pero botocore exige una para firmar SigV4.
DEFAULT_STORAGE_REGION = "us-east-1"


@dataclass
class StorageConfig:
    """Conexión al almacén de objetos (SeaweedFS, API S3).

    El endpoint apunta al nombre de servicio del compose: el gateway no publica ningún
    puerto en el host, así que solo la API lo alcanza y no existe forma de llegar a un
    archivo sin pasar por la autorización de FastAPI.
    """

    endpoint: str = field(default_factory=lambda: get_or_throw("STORAGE_ENDPOINT"))
    access_key: str = field(default_factory=lambda: get_or_throw("STORAGE_ACCESS_KEY"))
    secret_key: str = field(default_factory=lambda: get_or_throw("STORAGE_SECRET_KEY"))
    bucket: str = field(default_factory=lambda: get_or_default("STORAGE_BUCKET", DEFAULT_STORAGE_BUCKET))
    region: str = field(default_factory=lambda: get_or_default("STORAGE_REGION", DEFAULT_STORAGE_REGION))

    # Ventanas de validez de las URLs firmadas. Cortas a propósito: son credenciales de
    # un solo uso, y el navegador las consume de inmediato.
    download_ttl_seconds: int = 60
    upload_ttl_seconds: int = 300
