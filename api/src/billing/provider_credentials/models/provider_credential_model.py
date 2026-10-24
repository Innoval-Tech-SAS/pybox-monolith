"""Credenciales de la cuenta propia de la plataforma en una pasarela de facturación."""

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from billing.provider_credentials.enums.provider_credential_enums import (
    PlatformGatewayProvider,
)
from core.base.encrypted_credential_model import EncryptedCredentialModel


class PlatformGatewayCredentialModel(EncryptedCredentialModel):
    """Credenciales de la(s) cuenta(s) PROPIA(S) de PYBOX en una pasarela, usadas para
    cobrar la suscripción/consumo a las organizaciones (billing de la plataforma, no
    cobro de un deudor). Mismo diseño de cifrado que `messaging.provider_credentials`
    y `receivables.payment_gateways` (ver `EncryptedCredentialModel`). `country_code`
    NULL = credencial GLOBAL."""

    __tablename__ = "credenciales_pasarela_plataforma"
    __table_args__ = (
        Index(
            "uq_credencial_pasarela_plataforma_pais_proveedor",
            "codigo_pais",
            "proveedor",
            unique=True,
            postgresql_where=text("eliminado_en IS NULL"),
        ),
    )

    country_code: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("paises.codigo"), nullable=True, name="codigo_pais"
    )
    provider: Mapped[PlatformGatewayProvider] = mapped_column(
        ENUM(
            PlatformGatewayProvider,
            name="proveedor_pasarela_plataforma",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        name="proveedor",
    )
