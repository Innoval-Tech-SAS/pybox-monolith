import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database.database import Base


class SegmentExecutionModel(Base):
    __tablename__ = "ejecuciones_segmentos"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    segment_id: Mapped[int] = mapped_column(Integer, ForeignKey("segmentos.id"), nullable=False, index=True, name="id_segmento")
    mode: Mapped[str] = mapped_column(String, nullable=False, name="modo")
    file_name: Mapped[str | None] = mapped_column(String, nullable=True, name="nombre_archivo")
    file_path: Mapped[str | None] = mapped_column(String, nullable=True, name="ruta_archivo")
    rows: Mapped[int] = mapped_column(Integer, nullable=False, name="filas")
    columns: Mapped[list] = mapped_column(JSONB, nullable=False, name="columnas")
    executed_by: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False, name="ejecutado_por")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), name="fecha_creacion"
    )
