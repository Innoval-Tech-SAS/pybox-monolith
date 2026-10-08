import type { Invoice, TenantBillingStatus } from "@/types/billing/billing-types";

export interface BillingSummary {
  currentInvoice: Invoice | null;
  invoices: Invoice[];
  total: number;
  status: TenantBillingStatus | null;
}
