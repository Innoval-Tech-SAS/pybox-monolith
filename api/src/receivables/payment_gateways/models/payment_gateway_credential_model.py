import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel
from receivables.payment_gateways.enums.payment_gateway_enums import (
    ReceivablesGatewayProvider,
)


class OrganizationGatewayCredentialModel(BaseModel):
    """Credenciales de la cuenta PROPIA de una organización en una pasarela de pago,
    usadas para cobrarle a SUS deudores (la plataforma nunca las recibe ni dispersa).

    Mismo diseño de cifrado que `messaging.provider_credentials` y
    `billing.provider_credentials`: secretos cifrados individualmente en `secrets`
    (JSONB), no secretos en claro en `public_config`, `lookup_key` para resolver por
    identificador del proveedor cuando el webhook lo trae (ver skill `wompi-gateway`).

    A diferencia de las otras dos tablas, aquí NO existe el concepto de credencial
    global: `organization_id` es obligatorio, porque la cuenta de una pasarela siempre
    es de una empresa concreta, nunca "de la plataforma" ni "por defecto"."""

    __tablename__ = "credenciales_pasarela_organizacion"
    __table_args__ = (
        Index(
            "uq_credencial_pasarela_organizacion_org_proveedor",
            "id_organizacion",
            "proveedor",
            unique=True,
            postgresql_where=text("eliminado_en IS NULL"),
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("entidades.id"),
        nullable=False,
        index=True,
        name="id_organizacion",
    )
    provider: Mapped[ReceivablesGatewayProvider] = mapped_column(
        ENUM(
            ReceivablesGatewayProvider,
            name="proveedor_pasarela_organizacion",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        name="proveedor",
    )
    secrets: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, name="secretos"
    )
    public_config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, name="config_publica"
    )
    lookup_key: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, name="clave_busqueda"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, name="activo"
    )
