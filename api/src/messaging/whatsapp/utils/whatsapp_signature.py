"""Verificación HMAC de la firma del webhook de WhatsApp (Meta)."""

import hashlib
import hmac

from core.tools.config_tools import get_or_throw

_SIGNATURE_PREFIX = "sha256="


def verify_whatsapp_signature(raw_body: bytes, signature: str | None) -> bool:
    # pylint: disable=line-too-long
    """Verifica la firma del webhook de Meta.

    Algoritmo: HMAC-SHA256(rawBody, app_secret), header `X-Hub-Signature-256` con
    prefijo `sha256=`. Docs:
    https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint
    """
    # pylint: enable=line-too-long
    if not signature or not signature.startswith(_SIGNATURE_PREFIX):
        return False
    app_secret = get_or_throw("WHATSAPP_CLOUD_APP_SECRET")
    digest = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature[len(_SIGNATURE_PREFIX) :])
