import type { PaymentAttempt } from "@/types/billing/billing-types";

export interface InvoicePaymentAttemptsTableProps {
  attempts: PaymentAttempt[];
}
