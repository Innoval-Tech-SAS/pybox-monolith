from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel


class NotificationModel(AuditModel):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False, name="id_usuario"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, name="titulo")
    body: Mapped[str] = mapped_column(String(1000), nullable=False, name="cuerpo")
    category: Mapped[str] = mapped_column(String(100), nullable=False, name="categoria")
    notif_type: Mapped[str | None] = mapped_column(String(50), nullable=True, name="tipo", default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, name="leida")
    link: Mapped[str | None] = mapped_column(String(500), nullable=True, name="enlace")
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True, name="detalles")
