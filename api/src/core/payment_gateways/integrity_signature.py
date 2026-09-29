import hashlib


def build_concatenated_sha256_signature(*parts: str) -> str:
    """SHA256 en hexadecimal de la concatenacion (sin separadores) de `parts`, en el
    orden dado.

    Formula compartida por Bold (`{order_id}{amount}{currency}{secret}`, ver
    `billing/bold/utils/bold_client.py`) y Wompi (`{reference}{amount_in_cents}
    {currency}[{expiration_time}]{integrity_secret}`, ver skill `wompi-gateway` Paso 8):
    ambos firman igual (concatenar y aplicar SHA256), solo cambian los campos
    concatenados y cual es el secreto — eso lo decide cada llamador, no esta funcion."""
    raw = "".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
