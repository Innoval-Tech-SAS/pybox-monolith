import hashlib

from core.tools.config_tools import get_or_throw


def generate_integrity_hash(order_id: str, amount_pesos: int, currency: str) -> str:
    """
    Genera el hash de integridad Bold para una transaccion.

    Formula: SHA256(f"{order_id}{amount_pesos}{currency}{secret_key}")

    El Boton de pagos de Bold es un widget de frontend: no se hacen llamadas
    HTTP al servidor de Bold desde el backend. El backend solo genera este
    hash, que el frontend incluye en data-integrity-signature. DEBE calcularse
    en el servidor para proteger la llave secreta.

    amount_pesos es el total en pesos COP enteros (sin decimales).
    Docs: https://developers.bold.co/pagos-en-linea/boton-de-pagos/integracion-manual/integracion-manual#4-genera-un-hash-de-integridad
    """
    secret_key = get_or_throw("BOLD_SECRET_KEY")
    raw = f"{order_id}{amount_pesos}{currency}{secret_key}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
