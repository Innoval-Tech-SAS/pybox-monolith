import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class ReportModel(AuditModel):
    __tablename__ = "reportes"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    name: Mapped[str] = mapped_column(String, nullable=False, name="nombre")
    description: Mapped[str | None] = mapped_column(String, nullable=True, name="descripcion")
    report_config: Mapped[dict] = mapped_column(JSONB, nullable=False, name="configuracion_reporte")
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, index=True, name="id_organizacion"
    )
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True, name="id_entidad")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True, name="es_global")
    category: Mapped[str | None] = mapped_column(String, nullable=True, name="categoria")
