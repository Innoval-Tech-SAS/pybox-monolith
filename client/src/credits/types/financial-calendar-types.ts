import type { CreditWithPayments, PaymentSummary } from "@/credits/types/credit-types";

export type FinancialEventType = "upcoming" | "history";
export type FinancialPaymentStatus = "onTime" | "overdue" | "partialPaid" | "totalPaid";

export interface FinancialCalendarEvent {
  type: FinancialEventType;
  status: FinancialPaymentStatus;
  credit: CreditWithPayments;
  payment: PaymentSummary;
}

export interface StatusMeta {
  dotClass: string;
  chipClass: string;
  label: string;
  eventColor: string;
  eventTextColor: string;
}

/** Estilo del calendario para un tipo de crédito. Solo presentación. */
export interface CreditTypeStyle {
  /** Punto de color de la leyenda. */
  dotClass: string;
  /** Borde + fondo de la tarjeta del evento. */
  cardClass: string;
  /** Hex del círculo del día; FullCalendar no acepta clases de Tailwind ahí. */
  accent: string;
}
