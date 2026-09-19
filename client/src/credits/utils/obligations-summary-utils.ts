import type { CreditWithPayments, PaymentSummary } from "@/credits/types/credit-types";
import type { ObligationRow, ObligationsSummary } from "@/credits/types/obligations-types";
import { toValidDate } from "@/credits/utils/financial-calendar-utils";

const expectedAmount = (payment: PaymentSummary): number =>
  payment.principalPayment + payment.totalInterestAmount + payment.otherCharges;

const isSameMonth = (date: Date, reference: Date): boolean =>
  date.getFullYear() === reference.getFullYear() && date.getMonth() === reference.getMonth();

/** Próxima cuota sin pagar de un crédito, la más cercana por fecha límite. */
export const getNextPayment = (credit: CreditWithPayments): PaymentSummary | null => {
  const pending = credit.payments
    .filter((payment) => !payment.paymentDate)
    .map((payment) => ({ payment, date: toValidDate(payment.limitPayDate) }))
    .filter((entry): entry is { payment: PaymentSummary; date: Date } => entry.date !== null)
    .sort((a, b) => a.date.getTime() - b.date.getTime());

  return pending[0]?.payment ?? null;
};

/**
 * Resumen del mes en curso a partir de los créditos ya cargados.
 *
 * Se calcula en el front a propósito: `/credits/my-credits` ya trae todo lo necesario,
 * así que un endpoint de resumen sería una segunda vuelta al servidor por los mismos datos.
 */
export const buildObligationsSummary = (
  credits: CreditWithPayments[],
  reference: Date = new Date(),
): ObligationsSummary => {
  let monthTotal = 0;
  let dueTotal = 0;
  let overdueTotal = 0;
  const entities = new Set<string>();

  credits.forEach((credit) => {
    entities.add(credit.organizationName);
    overdueTotal += credit.overduePrincipalBalance;

    credit.payments.forEach((payment) => {
      const limit = toValidDate(payment.limitPayDate);
      if (!limit || !isSameMonth(limit, reference)) return;

      const amount = expectedAmount(payment);
      monthTotal += amount;
      // "Por vencer" es lo que todavía no se pagó dentro del mes.
      if (!payment.paymentDate) dueTotal += amount;
    });
  });

  return {
    monthTotal,
    dueTotal,
    overdueTotal,
    entityCount: entities.size,
    currencyCode: credits[0]?.currencyCode ?? "COP",
    periodLabel: reference.toLocaleDateString("es-CO", { month: "long", year: "numeric" }),
  };
};

/** Una fila de la tabla "Detalle de obligaciones". */
export const buildObligationRows = (credits: CreditWithPayments[]): ObligationRow[] =>
  credits.map((credit) => {
    const next = getNextPayment(credit);
    return {
      creditId: credit.id,
      creditNumber: credit.creditNumber,
      creditType: credit.creditType,
      entityName: credit.organizationName,
      currencyCode: credit.currencyCode,
      nextDueDate: next?.limitPayDate ?? null,
      installmentAmount: next ? expectedAmount(next) : 0,
      status: next?.status ?? null,
      isOverdue: credit.daysOverdueAtCutoff > 0,
    };
  });
