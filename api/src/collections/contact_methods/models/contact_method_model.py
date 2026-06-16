import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from collections.contact_methods.enums.contact_method_enums import ContactMethodType


class ContactMethodModel(AuditModel):
    __tablename__ = "metodos_contacto"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    contact_type: Mapped[ContactMethodType] = mapped_column(ENUM(ContactMethodType), nullable=False, name="tipo_contacto")
    contact_value: Mapped[str] = mapped_column(String, nullable=False, name="valor_contacto")
    debtor_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("deudores.id"), nullable=False, name="id_deudor"
    )
