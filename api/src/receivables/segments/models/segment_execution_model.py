import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel


class SegmentExecutionModel(BaseModel):
    __tablename__ = "ejecuciones_segmentos"

    segment_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("segmentos.id"),
        nullable=False,
        index=True,
        name="id_segmento",
    )
    mode: Mapped[str] = mapped_column(String, nullable=False, name="modo")
    file_name: Mapped[str | None] = mapped_column(
        String, nullable=True, name="nombre_archivo"
    )
    file_path: Mapped[str | None] = mapped_column(
        String, nullable=True, name="ruta_archivo"
    )
    rows: Mapped[int] = mapped_column(Integer, nullable=False, name="filas")
    columns: Mapped[list] = mapped_column(JSONB, nullable=False, name="columnas")
    executed_by: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        name="ejecutado_por",
        index=True,
    )
