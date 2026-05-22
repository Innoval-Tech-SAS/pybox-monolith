from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from base.audit_model import AuditModel
from debtors.enums.debtor_enums import DebtorType, DocumentTypes


class DebtorModel(AuditModel):
    __tablename__ = "deudores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    full_name: Mapped[str] = mapped_column(String, nullable=False, name="nombre_completo")
    debtor_type: Mapped[DebtorType] = mapped_column(ENUM(DebtorType), nullable=False, name="tipo_deudor")
    document_type: Mapped[DocumentTypes] = mapped_column(ENUM(DocumentTypes), nullable=False, name="tipo_documento")
    document_number: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True, name="numero_documento")
