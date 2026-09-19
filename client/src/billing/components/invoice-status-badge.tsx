import { Badge } from "@/ui/components/badge";
import type { InvoiceStatus } from "@/types/billing/billing-types";
import { INVOICE_STATUS_LABELS as STATUS_LABELS, INVOICE_STATUS_COLORS as STATUS_COLORS } from "../constants/invoice-status-labels";

export const InvoiceStatusBadge: React.FC<{ status: InvoiceStatus }> = ({ status }) => (
  <Badge color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Badge>
);
