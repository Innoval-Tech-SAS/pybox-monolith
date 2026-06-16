from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel


class AddressModel(AuditModel):
    __tablename__ = "direcciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    address: Mapped[str] = mapped_column(String, nullable=False, name="direccion")
    city: Mapped[str] = mapped_column(String, nullable=False, name="ciudad")
    state: Mapped[str] = mapped_column(String, nullable=False, name="departamento")
    country: Mapped[str] = mapped_column(String, nullable=False, name="pais")
    address_type: Mapped[str] = mapped_column(String, nullable=False, default="PRIMARY", name="tipo_direccion")
    debtor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deudores.id"), nullable=False, name="id_deudor"
    )
