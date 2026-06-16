import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from app_platform.countries.enums.country_enums import Nationality


class PortfolioModel(AuditModel):
    __tablename__ = "portafolios"

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        name="id",
    )
    name: Mapped[str] = mapped_column(String, nullable=False, name="nombre")
    description: Mapped[str | None] = mapped_column(String, nullable=True, name="descripcion")
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, index=True, name="id_organizacion"
    )
    country: Mapped[Nationality | None] = mapped_column(
        ENUM(Nationality, name="nationality"), nullable=True, name="pais"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
