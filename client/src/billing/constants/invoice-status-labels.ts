import type { BadgeColor } from "@/types/props/badge-props";
import type { InvoiceStatus } from "@/types/billing/billing-types";

export const INVOICE_STATUS_LABELS: Record<InvoiceStatus, string> = {
  BORRADOR: "Borrador",
  EMITIDA: "Emitida",
  PAGO_PENDIENTE: "Pago en proceso",
  VENCIDA: "Vencida",
  BLOQUEADA: "Bloqueada",
  PAGADA: "Pagada",
  CANCELADA: "Cancelada",
};

export const INVOICE_STATUS_COLORS: Record<InvoiceStatus, BadgeColor> = {
  BORRADOR: "light",
  EMITIDA: "info",
  PAGO_PENDIENTE: "warning",
  VENCIDA: "warning",
  BLOQUEADA: "error",
  PAGADA: "success",
  CANCELADA: "light",
};

/** Mismos tonos que INVOICE_STATUS_COLORS pero en hex, para charts (ApexCharts no acepta tokens de Badge). */
export const INVOICE_STATUS_CHART_COLORS: Record<InvoiceStatus, string> = {
  BORRADOR: "#d0d5dd",
  EMITIDA: "#465fff",
  PAGO_PENDIENTE: "#f79009",
  VENCIDA: "#f79009",
  BLOQUEADA: "#f04438",
  PAGADA: "#12b76a",
  CANCELADA: "#98a2b3",
};
