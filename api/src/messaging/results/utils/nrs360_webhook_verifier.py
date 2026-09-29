"""Verificación del token compartido del webhook de eventos de 360NRS."""

import hmac

from core.config.logger import logger
from core.tools.config_tools import get_or_default


def verify_nrs360_webhook_token(token: str | None) -> bool:
    """Verifica el token compartido del webhook de eventos de 360NRS.

    360NRS no firma sus notificaciones: la URL se configura a nivel de
    cuenta en su dashboard, así que el secreto viaja en esa URL
    (`.../results/webhook?token=<secreto>`).
    Se compara en tiempo constante contra `NRS360_WEBHOOK_TOKEN`.

    Si la variable no está configurada se rechaza todo: un webhook público sin
    verificación deja a cualquiera que conozca un id de envío cambiar el estado de
    entrega de un contacto de cualquier organización.
    """
    if not token:
        return False

    secret = get_or_default("NRS360_WEBHOOK_TOKEN", "").strip()
    if not secret:
        logger.error(
            "[results_webhook] NRS360_WEBHOOK_TOKEN no configurada: se "
            "rechaza el evento"
        )
        return False

    return hmac.compare_digest(secret.encode("utf-8"), token.strip().encode("utf-8"))
