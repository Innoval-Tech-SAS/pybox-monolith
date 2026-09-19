from dataclasses import dataclass

from core.tools.config_tools import get_or_default, get_or_throw
from messaging.ivr.constants.helena_defaults import DEFAULT_TIMEOUT_SECONDS


@dataclass(frozen=True)
class HelenaConfig:
    """Configuración de conexión a la API externa de Helena (llamadas IVR)."""

    base_url: str
    api_key: str
    timeout_seconds: int = int(DEFAULT_TIMEOUT_SECONDS)


def load_helena_config() -> HelenaConfig:
    """Carga la configuración de Helena desde variables de entorno.

    Se invoca de forma perezosa (en el primer envío IVR), no al importar el
    módulo, para no exigir las variables cuando la instalación no usa el canal
    de llamadas. `get_or_throw` lanza un error claro si faltan al momento de usar.
    """
    base_url = get_or_throw("HELENA_BASE_URL").strip().rstrip("/")
    api_key = get_or_throw("HELENA_API_TOKEN").strip()

    timeout_raw = get_or_default("HELENA_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    try:
        timeout_seconds = int(timeout_raw)
    except ValueError:
        timeout_seconds = int(DEFAULT_TIMEOUT_SECONDS)

    return HelenaConfig(base_url=base_url, api_key=api_key, timeout_seconds=timeout_seconds)
