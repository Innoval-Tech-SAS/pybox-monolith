export interface PaymentSummary {
  id: string;
  limitPayDate: string;
  paymentDate: string | null;
  paymentAmount: number;
  installmentNumber: number | null;
  principalPayment: number;
  totalInterestAmount: number;
  otherCharges: number;
  status?: string;
}

/** Estados de pago que expone el backend (enum PaymentStatus, valores en MAYÚSCULA). */
export const PAYMENT_STATUS = {
  PENDING: "PENDIENTE",
  RESCHEDULE_REQUESTED: "REPROGRAMACION_SOLICITADA",
  RESCHEDULED: "REPROGRAMADO",
  VALIDATION_REQUESTED: "VALIDACION_SOLICITADA",
  PAID: "PAGADO",
} as const;

export interface PaymentMethod {
  id: string;
  name: string;
  type: string;
  description: string | null;
  instructions: string | null;
  bankName: string | null;
  accountType: string | null;
  accountNumber: string | null;
  paymentLink: string | null;
  qrImageUrl: string | null;
}

/** Opción servida por GET /credits/types. El front no mantiene la lista ni sus etiquetas. */
export interface CreditTypeOption {
  value: string;
  label: string;
}

export interface CreditWithPayments {
  id: string;
  creditNumber: string;
  creditType: string;
  disbursedDate: string;
  totalCreditBalance: number;
  overduePrincipalBalance: number;
  daysOverdueAtCutoff: number;
  role: string;
  organizationName: string;
  currencyCode: string;
  payments: PaymentSummary[];
  paymentMethods: PaymentMethod[];
  isActive: boolean;
  settlementRequested: boolean;
}
