import type { PaymentSummary } from "@/credits/types/credit-types";

export interface WompiCheckoutFormProps {
  payment: PaymentSummary;
  currencyCode: string;
  onDone: () => void;
  onCancel: () => void;
}
