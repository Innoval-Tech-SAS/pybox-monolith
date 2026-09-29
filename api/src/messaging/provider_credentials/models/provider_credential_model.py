from sqlalchemy import Boolean, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel
from messaging.provider_credentials.enums.provider_credential_enums import MessagingCredentialProvider


class MessagingProviderCredentialModel(BaseModel):
    """Credenciales de un proveedor de mensajería (SMS/Email/WhatsApp) por país.

    Mismo diseño que las otras dos tablas de credenciales del proyecto (ver
    `billing.provider_credentials` y `receivables.payment_gateways`): secretos cifrados
    individualmente en `secrets` (JSONB), no secretos en claro en `public_config`,
    `lookup_key` para resolver por identificador del proveedor. `country_code` NULL =
    credencial GLOBAL (WhatsApp Cloud y NRS360 hoy usan una sola cuenta compartida)."""

    __tablename__ = "credenciales_mensajeria"
    __table_args__ = (
        Index(
            "uq_credencial_mensajeria_pais_proveedor",
            "codigo_pais", "proveedor",
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
    secrets: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, name="secretos")
    public_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, name="config_publica")
    lookup_key: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, name="clave_busqueda"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
