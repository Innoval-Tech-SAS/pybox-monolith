export type InvoiceStatus =
  | "DRAFT"
  | "ISSUED"
  | "PAYMENT_PENDING"
  | "OVERDUE"
  | "BLOCKED"
  | "PAID"
  | "CANCELLED";

export type PaymentAttemptStatus =
  | "ACTIVE"
  | "PROCESSING"
  | "PAID"
  | "EXPIRED"
  | "REJECTED"
  | "CANCELLED";

export type BillingLockStatus = "NONE" | "WARNING" | "PAYMENT_REQUIRED" | "BLOCKED";

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
  boldReference: string | null;
  boldLinkId: string | null;
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

/** Datos necesarios para renderizar el Boton de pagos Bold en el frontend. */
export interface PaymentLinkData {
  orderId: string;
  amount: number;
  currency: string;
  integritySignature: string;
  description: string;
  taxType: string;
  boldTax: string | null;
  attemptId: string;
  reused: boolean;
  apiKey: string;
  redirectionUrl: string;
}

export interface TenantBillingStatus {
  lockStatus: BillingLockStatus;
  activeInvoiceId: string | null;
  message: string | null;
}
