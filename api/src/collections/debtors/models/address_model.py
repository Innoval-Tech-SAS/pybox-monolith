import uuid
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from core.base.audit_model import AuditModel


class AddressModel(AuditModel):
    __tablename__ = "direcciones"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    address: Mapped[str] = mapped_column(String, nullable=False, name="direccion")
    city: Mapped[str] = mapped_column(String, nullable=False, name="ciudad")
    state: Mapped[str] = mapped_column(String, nullable=False, name="departamento")
    country: Mapped[str] = mapped_column(String, nullable=False, name="pais")
    address_type: Mapped[str] = mapped_column(String, nullable=False, default="PRIMARY", name="tipo_direccion")
    debtor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deudores.id"), nullable=False, name="id_deudor"
    )
