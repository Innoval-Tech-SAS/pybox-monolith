import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel


class WhatsAppOrgCredentialsModel(BaseModel):

    __tablename__ = "whatsapp_credenciales_organizacion"
    __table_args__ = (
        UniqueConstraint("id_organizacion", name="uq_whatsapp_credenciales_organizacion"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("entidades.id"),
        nullable=False,
        index=True,
        name="id_organizacion",
    )

    phone_number_id: Mapped[str] = mapped_column(
        String(50), nullable=False, name="id_numero_telefono"
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, name="nombre_visible"
    )

    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, name="activo"
    )
