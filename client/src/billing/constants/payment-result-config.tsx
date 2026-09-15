import { CheckCircle, XCircle, Clock, AlertTriangle } from "lucide-react";
import type { PaymentAttemptStatus } from "@/types/billing/billing-types";

/**
 * Resultado visual de un pago, independiente del proveedor. Bold llega por redirect con
 * su `bold-tx-status` (APPROVED/DECLINED/PENDING) y Mercado Pago se resuelve desde el
 * estado del intento; ambos terminan en uno de estos estados para reusar la misma UI.
 */
export type PaymentResultStatus = "APPROVED" | "DECLINED" | "PENDING" | "ERROR";

export interface PaymentResultConfig {
  icon: React.ReactNode;
  title: string;
  message: string;
  color: string;
}

export const PAYMENT_RESULT_CONFIG: Record<PaymentResultStatus, PaymentResultConfig> = {
  APPROVED: {
    icon: <CheckCircle size={56} className="text-success-500" />,
    title: "¡Pago exitoso!",
    message: "Tu pago fue procesado correctamente. Gracias por tu pago.",
    color: "text-success-600 dark:text-success-400",
  },
  DECLINED: {
    icon: <XCircle size={56} className="text-error-500" />,
    title: "Pago rechazado",
    message: "Tu pago no pudo ser procesado. Por favor intenta de nuevo o usa otro método de pago.",
    color: "text-error-600 dark:text-error-400",
  },
  PENDING: {
    icon: <Clock size={56} className="text-warning-500" />,
    title: "Pago en proceso",
    message: "Tu pago está siendo verificado. Te notificaremos cuando se confirme.",
    color: "text-warning-600 dark:text-warning-400",
  },
  ERROR: {
    icon: <AlertTriangle size={56} className="text-error-500" />,
    title: "No se pudo procesar",
    message: "Ocurrió un problema al procesar el pago. Verifica los datos de la tarjeta e intenta de nuevo.",
    color: "text-error-600 dark:text-error-400",
  },
};

export const PAYMENT_RESULT_DEFAULT: PaymentResultConfig = {
  icon: <Clock size={56} className="text-gray-400" />,
  title: "Estado desconocido",
  message: "No pudimos determinar el estado de tu pago. Revisa tu factura para más detalles.",
  color: "text-gray-600 dark:text-gray-400",
};

export const resolvePaymentResultConfig = (status: string): PaymentResultConfig =>
  PAYMENT_RESULT_CONFIG[status as PaymentResultStatus] ?? PAYMENT_RESULT_DEFAULT;

const ATTEMPT_STATUS_TO_RESULT: Record<PaymentAttemptStatus, PaymentResultStatus> = {
  PAGADO: "APPROVED",
  RECHAZADO: "DECLINED",
  EXPIRADO: "DECLINED",
  CANCELADO: "DECLINED",
  PROCESANDO: "PENDING",
  ACTIVO: "PENDING",
};

/** Mapea el estado del intento de pago (Mercado Pago) al resultado visual. */
export const attemptStatusToResult = (
  status: PaymentAttemptStatus | undefined,
): PaymentResultStatus => (status ? ATTEMPT_STATUS_TO_RESULT[status] : "PENDING");
