"""Verificación HMAC de la firma del webhook de Bold para `receivables`."""

import base64
import hashlib
import hmac


def verify_bold_webhook_signature(
    raw_body: bytes, signature: str | None, secret_key: str
) -> bool:
    """HMAC-SHA256(Base64(rawBody), secretKey), comparado contra el header
    `x-bold-signature` -- misma fórmula que `billing.bold.utils.bold_webhook_verifier`
    (developers.bold.co/webhook), pero resuelta contra el `secret_key` de la cuenta
    Bold de la ORGANIZACIÓN (no la cuenta compartida de PYBOX en `billing`). En modo
    sandbox Bold firma con una llave secreta vacía, por lo que `secret_key` puede
    llegar vacío sin que eso sea un error."""
    if not signature:
        return False
    encoded = base64.b64encode(raw_body)
    digest = hmac.new(secret_key.encode("utf-8"), encoded, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)
