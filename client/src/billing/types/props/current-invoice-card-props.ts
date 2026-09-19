import type { Invoice } from "@/types/billing/billing-types";

export interface CurrentInvoiceCardProps {
  invoice: Invoice;
  onViewDetail: () => void;
}
