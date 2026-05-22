from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel
from contact_methods.enums.contact_method_enums import ContactMethodType


class ContactMethodModel(AuditModel):
    __tablename__ = "metodos_contacto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    contact_type: Mapped[ContactMethodType] = mapped_column(ENUM(ContactMethodType), nullable=False, name="tipo_contacto")
    contact_value: Mapped[str] = mapped_column(String, nullable=False, name="valor_contacto")
    debtor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deudores.id"), nullable=False, name="id_deudor"
    )
