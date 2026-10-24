import type { InvoiceStatus } from "@/types/billing/billing-types";

/** Estados en los que una factura todavia admite iniciar un pago. */
export const PAYABLE_INVOICE_STATUSES: InvoiceStatus[] = ["EMITIDA", "PAGO_PENDIENTE", "VENCIDA", "BLOQUEADA"];

/** Estados finales: ya no admiten reintentos ni un nuevo enlace de pago. */
export const TERMINAL_INVOICE_STATUSES: InvoiceStatus[] = ["PAGADA", "CANCELADA"];
