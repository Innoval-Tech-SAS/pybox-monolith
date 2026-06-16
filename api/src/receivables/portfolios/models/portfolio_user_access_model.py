import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class PortfolioUserAccessModel(AuditModel):
    __tablename__ = "accesos_usuario_portafolio"
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_portafolio", name="uq_acceso_usuario_portafolio"),
        Index("ix_acl_org_user_active", "id_organizacion", "id_usuario", "activo"),
        Index("ix_acl_portfolio_user_active", "id_portafolio", "id_usuario", "activo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True, name="id_usuario"
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("entidades.id"), nullable=False, index=True, name="id_organizacion"
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("portafolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        name="id_portafolio",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, name="activo")
    granted_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, name="otorgado_por"
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, name="revocado_en"
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, name="otorgado_en"
    )
