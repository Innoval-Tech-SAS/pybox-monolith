"""Descifrado y fusión de una credencial cifrada de proveedor externo."""

from core.security.services.encrypt_service import encrypt_service


def decrypt_credential_values(secrets: dict, public_config: dict) -> dict[str, str]:
    """Descifra `secrets` y los mezcla sobre `public_config`.

    Compartido por los 3 dominios con credenciales cifradas de proveedor externo
    (`billing.provider_credentials`, `messaging.provider_credentials`,
    `receivables.payment_gateways`); cada uno arma con el resultado su propio
    dataclass `Decrypted*Credential`.
    """
    decrypted = {
        key: encrypt_service.decrypt_to_str(token)
        for key, token in (secrets or {}).items()
    }
    return {**(public_config or {}), **decrypted}
