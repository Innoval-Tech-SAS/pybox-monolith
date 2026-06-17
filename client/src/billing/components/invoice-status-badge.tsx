import { Badge } from "@/ui/components/badge/badge";
import type { BadgeColor } from "@/types/props/badge-props";
import type { InvoiceStatus } from "@/types/billing/billing-types";

const STATUS_LABELS: Record<InvoiceStatus, string> = {
  DRAFT: "Borrador",
  ISSUED: "Emitida",
  PAYMENT_PENDING: "Pago en proceso",
  OVERDUE: "Vencida",
  BLOCKED: "Bloqueada",
  PAID: "Pagada",
  CANCELLED: "Cancelada",
};

const STATUS_COLORS: Record<InvoiceStatus, BadgeColor> = {
  DRAFT: "light",
  ISSUED: "info",
  PAYMENT_PENDING: "warning",
  OVERDUE: "warning",
  BLOCKED: "error",
  PAID: "success",
  CANCELLED: "light",
};

export const InvoiceStatusBadge: React.FC<{ status: InvoiceStatus }> = ({ status }) => (
  <Badge color={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</Badge>
);
