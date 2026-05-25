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
