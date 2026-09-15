import type { PaymentLinkData } from "@/types/billing/billing-types";

export interface InvoicePaymentSectionProps {
  paymentLink: PaymentLinkData | null;
  paying: boolean;
  onPay: () => void;
  onMercadoPagoCharge: (
    token: string,
    paymentMethodId: string,
    paymentTypeId: string,
    installments: number,
  ) => Promise<void>;
}
