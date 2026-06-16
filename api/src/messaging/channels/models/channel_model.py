from decimal import Decimal

from sqlalchemy import Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from messaging.channels.enums.channel_enums import ChannelName, Currency


class ChannelModel(AuditModel):

    __tablename__ = "canales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, name="id_canal")

    name: Mapped[ChannelName] = mapped_column(
        Enum(ChannelName), nullable=False, unique=True, index=True, name="nombre"
    )

    currency: Mapped[Currency] = mapped_column(
        Enum(Currency), nullable=False, default=Currency.COP, name="moneda"
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, name="precio_unitario"
    )

    description: Mapped[str] = mapped_column(String(255), nullable=False, name="descripcion")
