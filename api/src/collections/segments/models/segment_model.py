import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class SegmentModel(AuditModel):
    __tablename__ = "segmentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    name: Mapped[str] = mapped_column(String, nullable=False, name="nombre")
    description: Mapped[str | None] = mapped_column(String, nullable=True, name="descripcion")
    filter_criteria: Mapped[dict] = mapped_column(JSONB, nullable=False, name="criterios_filtro")
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, index=True, name="id_organizacion"
    )
