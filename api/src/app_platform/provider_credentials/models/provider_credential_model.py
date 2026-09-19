from sqlalchemy import Boolean, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel
from app_platform.provider_credentials.enums.provider_credential_enums import CredentialProvider


class ProviderCredentialModel(BaseModel):
    """Credenciales de un proveedor externo (envío o pasarela) por país.

    Diseño: los valores SECRETOS van cifrados individualmente en `secrets` (JSONB,
    cada valor es un token de encrypt_service; nunca en claro) y se descifran solo al
    enviar/cobrar. Los valores NO secretos (public_key de MP, sender de SMS, waba_id)
    van en claro en `public_config`. `lookup_key` (indexado, en claro) permite resolver
    el país por un identificador del proveedor — p. ej. el application_id de MP en el
    webhook, que se busca por igualdad antes de verificar la firma.

    `country_code` NULL = credencial GLOBAL (aplica a todos los países). Sirve a
    proveedores hoy compartidos (WhatsApp usa una sola app/WABA; NRS360 una sola
    cuenta), con override por país cuando se configure uno específico.
    """

    __tablename__ = "credenciales_proveedor"
    __table_args__ = (
        # Único parcial (solo entre credenciales vivas): con soft-delete, una credencial
        # borrada no debe bloquear volver a configurar el mismo país+proveedor.
        Index(
            "uq_credencial_pais_proveedor",
            "codigo_pais", "proveedor",
            unique=True,
            postgresql_where=text("eliminado_en IS NULL"),
        ),
    )

    country_code: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("paises.codigo"), nullable=True, name="codigo_pais"
    )
    provider: Mapped[CredentialProvider] = mapped_column(
        ENUM(CredentialProvider, name="proveedor_credencial", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        name="proveedor",
    )
    secrets: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, name="secretos")
    public_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, name="config_publica")
    lookup_key: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True, name="clave_busqueda"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
