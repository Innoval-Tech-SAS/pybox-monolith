import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import BaseModel
from receivables.portfolios.enums.portfolio_document_enums import (
    PortfolioDocumentCategory,
)


class PortfolioDocumentModel(BaseModel):
    """Archivo asociado a un portafolio: exportación de un segmento o archivo fuente de
    una carga.

    Tabla de unión por relación, misma solución que `documentos_deudor`: reemplaza
    al par `documentos.ambito='PORTAFOLIO' + documentos.id_dueno`. Las tres FK son
    reales y unidireccionales, así que no hay ciclo y no hace falta `use_alter`.
    """

    __tablename__ = "documentos_portafolio"

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("portafolios.id"),
        nullable=False,
        index=True,
        name="id_portafolio",
    )
    # Denormalizado desde el portafolio: aísla por organización sin tener que
    # resolver el portafolio en cada consulta, mismo criterio que
    # StatementModel.organization_id.
    # Es un atributo derivado de `portafolios.id_organizacion`: la coherencia la
    # garantiza el Service, que lo lee del portafolio ya cargado al insertar y
    # nunca lo actualiza después (un portafolio no cambia de entidad dueña).
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("entidades.id"),
        nullable=False,
        index=True,
        name="id_organizacion",
    )
    category: Mapped[PortfolioDocumentCategory] = mapped_column(
        ENUM(
            PortfolioDocumentCategory,
            name="categoria_documento_portafolio",
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=False,
        name="categoria",
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("documentos.id"),
        nullable=False,
        unique=True,
        name="id_documento",
    )
