import uuid
from datetime import datetime

from sqlalchemy import DateTime, Double, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from core.base.audit_model import AuditModel


class PaymentModel(AuditModel):
    __tablename__ = "pagos"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    limit_pay_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, name="fecha_limite_pago")
    payment_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, name="fecha_pago")
    payment_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="monto_pago")
    installment_number: Mapped[int | None] = mapped_column(Integer, nullable=True, name="numero_cuota")
    principal_payment: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="abono_capital")
    current_interest_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="interes_corriente")
    overdue_interest_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="interes_mora")
    life_insurance_charge: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="seguro_vida")
    vehicle_insurance_charge: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="seguro_vehiculo")
    insurances_total: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="seguros_totales")
    other_charges: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="otros_cargos")
    total_interest_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="total_intereses")
    other_concepts_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="otros_conceptos")
    vat: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="iva")
    commission_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="comision")
    platform_fee: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="fee_plataforma")
    condonation_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="condonacion_aplicada")
    discount_amount: Mapped[float] = mapped_column(Double, nullable=False, default=0.0, name="descuento_aplicado")
    amount_uvr: Mapped[float | None] = mapped_column(Double, nullable=True, name="monto_uvr")
    uvr_quote_at_payment: Mapped[float | None] = mapped_column(Double, nullable=True, name="cotizacion_uvr_pago")
    credit_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("creditos.id"), nullable=False, index=True, name="id_credito"
    )
