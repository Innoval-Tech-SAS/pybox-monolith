"""Verificación HMAC de la firma del webhook de Helena."""

import hashlib
import hmac

from core.config.logger import logger
from core.tools.config_tools import get_or_default
from messaging.ivr.constants.helena_defaults import UNSET


def verify_helena_signature(raw_body: bytes, signature: str | None) -> bool:
    """Verifica la firma del webhook de Helena.

    Algoritmo: `HMAC-SHA256(rawBody, secret)` en hexadecimal, comparado contra
    el header `X-Helena-Signature`. Helena firma exactamente los bytes que
    envía (`JSON.stringify(body)` en
    `helena-reporting/.../webhooks.service.ts:signPayload`), así que hay que
    verificar sobre el cuerpo crudo y no sobre el dict ya parseado.

    A diferencia del webhook de Bold, aquí el cuerpo **no** se codifica en
    base64 antes de firmar.

    Si `HELENA_WEBHOOK_SECRET` no está configurada se rechaza todo: un webhook
    público sin verificación deja cualquiera escribir resultados de llamadas.
    """
    if not signature:
        return False

    secret = get_or_default("HELENA_WEBHOOK_SECRET", UNSET).strip()
    if not secret:
        logger.error(
            "[ivr_webhook] HELENA_WEBHOOK_SECRET no configurada: se rechaza el evento"
        )
        return False

    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature.strip())
