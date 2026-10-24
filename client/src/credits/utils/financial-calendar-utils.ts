import type { CreditWithPayments, PaymentSummary } from "@/credits/types/credit-types";
import type { FinancialCalendarEvent, FinancialPaymentStatus } from "@/credits/types/financial-calendar-types";
import type { EventInput } from "@fullcalendar/core";
import { getCreditTypeStyle } from "@/constants/credits/financial-calendar";
import { formatShortDate } from "@/utils/format-date";
import { formatCurrency } from "@/utils/format-currency";

export const toValidDate = (value: string | null): Date | null => {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
};

export const toDateOnlyIso = (d: Date): string => {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
};

export const isPastDue = (limitPayDate: string): boolean => {
  const limit = toValidDate(limitPayDate);
  if (!limit) return false;
  const now = new Date();
  const endOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
  return limit.getTime() < endOfToday.getTime();
};

const getExpectedPayment = (p: PaymentSummary): number =>
  p.principalPayment + p.totalInterestAmount + p.otherCharges;

/**
 * Monto que muestra la tarjeta del calendario: lo pagado si ya se pagó, lo esperado
 * si todavía está por vencer.
 */
export const getEventAmount = (event: FinancialCalendarEvent): number =>
  event.type === "history" ? event.payment.paymentAmount : getExpectedPayment(event.payment);

export const isPartialPayment = (p: PaymentSummary): boolean => {
  const expected = getExpectedPayment(p);
  return expected > 0 && p.paymentAmount > 0 && p.paymentAmount < expected;
};

export const formatPaymentDate = (value: string | null): string =>
  formatShortDate(value, "Sin fecha");

export const formatCreditCurrency = (amount: number, code: string): string =>
  formatCurrency(amount, code || "COP", { maximumFractionDigits: 2 });

export const buildFinancialCalendarEvents = (credits: CreditWithPayments[]): EventInput[] => {
  const events: EventInput[] = [];

  credits.forEach((credit) => {
    const candidates = credit.payments
      .filter((p) => !p.paymentDate)
      .map((p) => ({ p, d: toValidDate(p.limitPayDate) }))
      .filter((x) => !!x.d)
      .sort((a, b) => a.d!.getTime() - b.d!.getTime());

    // El color del evento sale del TIPO de crédito, que es el eje de la leyenda del
    // calendario. El estado del pago se comunica en el chip del detalle, no acá.
    const typeStyle = getCreditTypeStyle(credit.creditType);

    const next = candidates[0];
    if (next?.d) {
      const status: FinancialPaymentStatus = isPastDue(next.p.limitPayDate) ? "overdue" : "onTime";
      events.push({
        id: `upcoming-${credit.id}-${next.p.id}`,
        title: credit.organizationName,
        date: toDateOnlyIso(next.d),
        color: typeStyle.accent,
        extendedProps: { type: "upcoming", status, credit, payment: next.p } as FinancialCalendarEvent,
      });
    }

    credit.payments
      .filter((p) => !!p.paymentDate)
      .forEach((p) => {
        const paidDate = toValidDate(p.paymentDate);
        if (!paidDate) return;
        const status: FinancialPaymentStatus = isPartialPayment(p) ? "partialPaid" : "totalPaid";
        events.push({
          id: `history-${credit.id}-${p.id}`,
          title: credit.organizationName,
          date: toDateOnlyIso(paidDate),
          color: typeStyle.accent,
          extendedProps: { type: "history", status, credit, payment: p } as FinancialCalendarEvent,
        });
      });
  });

  return events;
};
