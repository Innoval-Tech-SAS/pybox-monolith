from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel
from receivables.debtors.enums.debtor_enums import DebtorType


class DebtorModel(BaseModel):
    __tablename__ = "deudores"

    full_name: Mapped[str] = mapped_column(String, nullable=False, name="nombre_completo")
    debtor_type: Mapped[DebtorType] = mapped_column(
        ENUM(DebtorType, name="tipo_deudor", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        name="tipo_deudor",
    )
    document_type: Mapped[str] = mapped_column(
        String(40), ForeignKey("tipos_documento.codigo"), nullable=False, name="tipo_documento"
    )
    document_number: Mapped[str] = mapped_column(String, nullable=False, name="numero_documento")
    document_number_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True, name="numero_documento_hash")
