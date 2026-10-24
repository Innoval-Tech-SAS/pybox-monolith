import type { PaymentLinkData } from "@/types/billing/billing-types";

export interface MercadoPagoCardFormProps {
  data: PaymentLinkData;
  onCharge: (
    token: string,
    paymentMethodId: string,
    paymentTypeId: string,
    installments: number,
  ) => Promise<void>;
}
