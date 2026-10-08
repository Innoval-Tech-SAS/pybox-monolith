"""Credenciales de un proveedor de mensajería (SMS/Email/WhatsApp) por país."""

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from core.base.encrypted_credential_model import EncryptedCredentialModel
from messaging.provider_credentials.enums.provider_credential_enums import (
    MessagingCredentialProvider,
)


class MessagingProviderCredentialModel(EncryptedCredentialModel):
    """Credenciales de un proveedor de mensajería (SMS/Email/WhatsApp) por país.

    Mismo diseño que las otras dos tablas de credenciales del proyecto (ver
    `billing.provider_credentials` y `receivables.payment_gateways`, y
    `EncryptedCredentialModel` para las columnas compartidas). `country_code` NULL =
    credencial GLOBAL (WhatsApp Cloud y NRS360 hoy usan una sola cuenta compartida)."""

    __tablename__ = "credenciales_mensajeria"
    __table_args__ = (
        Index(
            "uq_credencial_mensajeria_pais_proveedor",
            "codigo_pais",
            "proveedor",
            unique=True,
            postgresql_where=text("eliminado_en IS NULL"),
        ),
    )

    country_code: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("paises.codigo"), nullable=True, name="codigo_pais"
    )
    provider: Mapped[MessagingCredentialProvider] = mapped_column(
        ENUM(
            MessagingCredentialProvider,
            name="proveedor_credencial_mensajeria",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        name="proveedor",
    )
