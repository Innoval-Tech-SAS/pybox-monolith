from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from platform.countries.enums.country_enums import UserDocumentType
from collections.debtors.enums.debtor_enums import DebtorType


class DebtorModel(AuditModel):
    __tablename__ = "deudores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, name="id")
    full_name: Mapped[str] = mapped_column(String, nullable=False, name="nombre_completo")
    debtor_type: Mapped[DebtorType] = mapped_column(ENUM(DebtorType), nullable=False, name="tipo_deudor")
    document_type: Mapped[UserDocumentType] = mapped_column(ENUM(UserDocumentType), nullable=False, name="tipo_documento")
    document_number: Mapped[str] = mapped_column(String, nullable=False, name="numero_documento")
    document_number_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True, name="numero_documento_hash")
