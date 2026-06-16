import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import ENUM, UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base.audit_model import AuditModel
from collections.credits.enums.credit_enums import CreditTypes


class CreditModel(AuditModel):
    __tablename__ = "creditos"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, name="id")
    credit_number: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True, name="numero_credito")
    credit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, name="fecha_credito")
    credit_type: Mapped[CreditTypes] = mapped_column(ENUM(CreditTypes), nullable=False, name="tipo_credito")
    agreed_interest_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="tasa_interes_pactada")
    balance_disbursed: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="saldo_desembolsado")
    disbursed_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, name="fecha_desembolso")
    court_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, name="fecha_corte")
    initial_term: Mapped[int] = mapped_column(Integer, nullable=False, name="plazo_inicial")
    total_credit_balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="saldo_total_credito")
    overdue_principal_balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="saldo_capital_mora")
    current_interest: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="interes_corriente")
    overdue_interest: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="interes_mora")
    other_concepts: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="otros_conceptos")
    overdue_installments: Mapped[int] = mapped_column(Integer, nullable=False, default=0, name="cuotas_en_mora")
    days_overdue_at_cutoff: Mapped[int] = mapped_column(Integer, nullable=False, default=0, name="dias_mora_al_corte")
    amortization_system: Mapped[str | None] = mapped_column(String, nullable=True, name="sistema_amortizacion")
    charged_effective_annual_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=0.0, name="tasa_efectiva_anual_cobrada")
    pending_installments: Mapped[int] = mapped_column(Integer, nullable=False, default=0, name="cuotas_pendientes")
    insurance_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="seguros_totales")
    commission_accum: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="comision_acumulada")
    platform_fee_accum: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="fee_plataforma_acumulado")
    vat_accum: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="iva_acumulado")
    subproduct: Mapped[str | None] = mapped_column(String, nullable=True, name="subproducto")
    uvr_last_quote: Mapped[float | None] = mapped_column(Numeric(12, 6), nullable=True, name="uvr_ultima_cotizacion")
    condonations_accum: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="condonaciones_acumuladas")
    discounts_accum: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0, name="descuentos_acumulados")

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("portafolios.id"), nullable=False, name="id_portafolio"
    )
    debtor_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("deudores.id"), nullable=False, name="id_deudor")
    codebtor_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("deudores.id"), nullable=True, name="id_codeudor")
