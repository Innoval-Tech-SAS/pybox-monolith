export type InvoiceStatus =
  | "BORRADOR"
  | "EMITIDA"
  | "PAGO_PENDIENTE"
  | "VENCIDA"
  | "BLOQUEADA"
  | "PAGADA"
  | "CANCELADA";

export type PaymentAttemptStatus =
  | "ACTIVO"
  | "PROCESANDO"
  | "PAGADO"
  | "EXPIRADO"
  | "RECHAZADO"
  | "CANCELADO";

export type BillingLockStatus = "NINGUNO" | "ADVERTENCIA" | "PAGO_REQUERIDO" | "BLOQUEADO";

export type PaymentProviderName = "BOLD" | "MERCADO_PAGO";

export interface InvoiceItem {
  id: string;
  invoiceId: string;
  campaignId: string | null;
  campaignName: string;
  channelId: string;
  channelName: string;
  baseCurrency: string;
  unitPriceBase: string;
  quantity: number;
  subtotalBase: string;
}

export interface PaymentAttempt {
  id: string;
  invoiceId: string;
  attemptNumber: number;
  provider: PaymentProviderName;
  providerReference: string | null;
  providerLinkId: string | null;
  paymentUrl: string | null;
  status: PaymentAttemptStatus;
  createdAt: string;
}

export interface Invoice {
  id: string;
  organizationId: string;
  periodYear: number;
  periodMonth: number;
  baseCurrency: string;
  billingCurrency: string;
  exchangeRate: string;
  subtotalBaseAmount: string;
  subtotalBillingAmount: string;
  taxType: string;
  taxRate: string;
  taxAmount: string;
  totalAmount: string;
  status: InvoiceStatus;
  issuedAt: string | null;
  dueAt: string | null;
  blockAt: string | null;
  paidAt: string | null;
  createdAt: string;
  updatedAt: string | null;
  items: InvoiceItem[];
  attempts: PaymentAttempt[];
}

export interface AdminInvoice extends Invoice {
  organizationName: string;
}

export interface CurrentInvoiceResponse {
  invoice: Invoice | null;
}

export interface ListInvoicesResponse {
  invoices: Invoice[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface AdminListInvoicesResponse {
  invoices: AdminInvoice[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

/** Datos especificos de Bold dentro de providerPayload (ver PaymentLinkData). */
export interface BoldProviderPayload {
  apiKey: string;
  integritySignature: string;
  redirectionUrl: string;
  boldTax: string | null;
}

/** Datos especificos de Mercado Pago dentro de providerPayload (Orders API, modo manual). */
export interface MercadoPagoProviderPayload {
  publicKey: string;
  orderId: string;
  clientToken: string | null;
}

/** Respuesta de POST /billing/invoices/{id}/payment-link; providerPayload varia segun provider. */
export interface PaymentLinkData {
  provider: PaymentProviderName;
  orderId: string;
  amount: number;
  currency: string;
  description: string;
  taxType: string;
  attemptId: string;
  reused: boolean;
  providerPayload: BoldProviderPayload | MercadoPagoProviderPayload | Record<string, unknown>;
}

export interface TenantBillingStatus {
  lockStatus: BillingLockStatus;
  activeInvoiceId: string | null;
  message: string | null;
}
