import type { AdminInvoice } from "@/types/billing/billing-types";

export interface AdminInvoiceListTableProps {
  invoices: AdminInvoice[];
  onViewDetail: (invoiceId: string) => void;
}
