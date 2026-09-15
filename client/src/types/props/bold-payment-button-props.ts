import type { PaymentLinkData } from "@/types/billing/billing-types";

export interface BoldPaymentButtonProps {
  data: PaymentLinkData;
  /** Estilo del boton: "dark"|"light" + "S"|"M"|"L", ej. "dark-L" */
  style?: string;
}
