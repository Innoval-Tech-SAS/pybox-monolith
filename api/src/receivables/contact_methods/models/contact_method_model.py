import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel
from receivables.contact_methods.enums.contact_method_enums import ContactMethodType


class ContactMethodModel(BaseModel):
    __tablename__ = "metodos_contacto"

    contact_type: Mapped[ContactMethodType] = mapped_column(
        ENUM(
            ContactMethodType,
            name="tipo_metodo_contacto",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        name="tipo_metodo_contacto",
    )
    contact_value: Mapped[str] = mapped_column(
        String, nullable=False, name="metodo_contacto"
    )
    debtor_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("deudores.id"),
        nullable=False,
        index=True,
        name="id_deudor",
    )
