"""Firma de integridad y verificación de eventos webhook de Wompi."""

import hmac
from typing import Any

from core.payment_gateways.integrity_signature import (
    build_concatenated_sha256_signature,
)


def build_integrity_signature(
    reference: str,
    amount_in_cents: int,
    currency: str,
    integrity_secret: str,
    expiration_time: str | None = None,
) -> str:
    """SHA256(reference + amount_in_cents + currency + [expiration_time +]
    secret), sin separadores (skill `wompi-gateway`, Paso 8). Se calcula SIEMPRE
    en el servidor: nunca en el frontend, expondria `integrity_secret`."""
    parts = [reference, str(amount_in_cents), currency]
    if expiration_time is not None:
        parts.append(expiration_time)
    parts.append(integrity_secret)
    return build_concatenated_sha256_signature(*parts)


def _resolve_dotted_path(data: dict[str, Any], path: str) -> Any:
    value: Any = data
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(path)
        value = value[part]
    return value


def verify_webhook_checksum(event_body: dict[str, Any], events_secret: str) -> bool:
    """Verifica `X-Event-Checksum`/`signature.checksum` siguiendo `signature.properties`
    del propio evento — NO un orden fijo, la doc de Wompi dice explicitamente que puede
    cambiar (skill `wompi-gateway`, Paso 7):

    1. Concatenar, en el orden de `signature.properties`, los valores de esas
       propiedades dentro de `data` (rutas con punto, ej. "transaction.id").
    2. Concatenar el `timestamp` (unix, como entero).
    3. Concatenar el `events_secret` de la organizacion duena de la transaccion.
    4. SHA256 de todo lo anterior, comparado en tiempo constante contra el checksum
       recibido (evita timing attacks en la comparacion).
    """
    signature = event_body.get("signature") or {}
    properties = signature.get("properties") or []
    received_checksum = str(signature.get("checksum") or "")
    timestamp = event_body.get("timestamp")
    data = event_body.get("data") or {}

    if not properties or not received_checksum or timestamp is None:
        return False

    try:
        concatenated_values = "".join(
            str(_resolve_dotted_path(data, prop)) for prop in properties
        )
    except KeyError:
        return False

    computed_checksum = build_concatenated_sha256_signature(
        concatenated_values, str(timestamp), events_secret
    )
    return hmac.compare_digest(computed_checksum.lower(), received_checksum.lower())
