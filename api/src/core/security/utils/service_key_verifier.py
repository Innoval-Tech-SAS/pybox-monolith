import hmac

from core.config.logger import logger
from core.tools.config_tools import get_or_default

N8N_SERVICE_KEY_ENV = "N8N_SERVICE_KEY"


def verify_n8n_service_key(key: str | None) -> bool:
    """Verifica la llave de servicio con la que n8n llama a los endpoints internos de la API.

    La llave viaja en el header ``X-Service-Key`` y se compara en tiempo constante contra
    ``N8N_SERVICE_KEY``. Estos endpoints leen datos de deudores sin sesión de usuario, así
    que sin llave válida no se responde nada.

    Si la variable no está configurada se rechaza todo: aceptar una llave vacía dejaría el
    endpoint abierto a cualquiera con acceso de red a la API.
    """
    if not key:
        return False

    secret = get_or_default(N8N_SERVICE_KEY_ENV, "").strip()
    if not secret:
        logger.error("[service_key] %s no configurada: se rechaza la llamada interna", N8N_SERVICE_KEY_ENV)
        return False

    return hmac.compare_digest(secret.encode("utf-8"), key.strip().encode("utf-8"))
