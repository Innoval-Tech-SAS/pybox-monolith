import type { PaymentResultStatus } from "@/billing/types/payment-result-types";

export interface PaymentResultModalProps {
  isOpen: boolean;
  status: PaymentResultStatus;
  reference?: string | null;
  onClose: () => void;
  /** Solo se muestra en rechazo/error, para reintentar sin cerrar el formulario. */
  onRetry?: () => void;
}
