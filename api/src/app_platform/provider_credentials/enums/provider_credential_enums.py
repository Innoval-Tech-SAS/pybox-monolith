from enum import StrEnum


class CredentialProvider(StrEnum):
    """Proveedores externos cuyas credenciales viven cifradas en DB por país.

    Solo el identificador de marca queda en el idioma del proveedor (no se traduce un
    nombre propio); mayúscula y snake_case por convención general de enums del
    proyecto. NRS360 se separa por canal (SMS/Email) porque cada uno tiene su propia
    cuenta/token en la cuenta 360nrs. Es una clave interna nuestra (fila de
    `credenciales_proveedor`) — no se compara contra ningún payload externo, así que
    renombrarla no rompe ninguna integración."""

    NRS360_SMS = "360NRS_SMS"
    NRS360_EMAIL = "360NRS_EMAIL"
    WHATSAPP_CLOUD = "WHATSAPP_CLOUD"
    MERCADOPAGO = "MERCADOPAGO"
    BOLD = "BOLD"
