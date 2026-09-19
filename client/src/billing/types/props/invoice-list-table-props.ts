import type { Invoice } from "@/types/billing/billing-types";

export interface InvoiceListTableProps {
  invoices: Invoice[];
  onViewDetail: (invoiceId: string) => void;
}
