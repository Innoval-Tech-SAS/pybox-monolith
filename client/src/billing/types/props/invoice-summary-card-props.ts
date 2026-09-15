import type { AdminInvoice, Invoice } from "@/types/billing/billing-types";

export interface InvoiceSummaryCardProps {
  invoice: Invoice | AdminInvoice;
  isAdminMode: boolean;
  syncing: boolean;
  onSync: () => void;
}
