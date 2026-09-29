"""Proveedores de mensajería con credenciales cifradas en DB por país."""

from enum import StrEnum


class MessagingCredentialProvider(StrEnum):
    """Proveedores de mensajería cuyas credenciales viven cifradas en DB por país.

    Separado de los proveedores de pasarela de pago (ver `billing.provider_credentials`
    y `receivables.payment_gateways`): son contextos sin relación entre sí que antes
    compartían una sola tabla/enum."""

    NRS360_SMS = "360NRS_SMS"
    NRS360_EMAIL = "360NRS_EMAIL"
    WHATSAPP_CLOUD = "WHATSAPP_CLOUD"
