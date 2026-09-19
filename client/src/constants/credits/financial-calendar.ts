import type {
  CreditTypeStyle,
  FinancialPaymentStatus,
  StatusMeta,
} from "@/credits/types/financial-calendar-types";

/**
 * Color por tipo de crédito: es el eje que colorea el calendario del titular.
 *
 * Solo estilo — el código y la etiqueta legible los sirve el backend
 * (`GET /credits/types`). Las claves son los códigos del enum `CreditTypes`.
 */
export const CREDIT_TYPE_STYLES: Record<string, CreditTypeStyle> = {
  TARJETA_CREDITO: {
    dotClass: "bg-blue-500",
    cardClass: "border-blue-200 bg-blue-50 dark:border-blue-900 dark:bg-blue-950",
    accent: "#3b82f6",
  },
  CREDITO_VEHICULO: {
    dotClass: "bg-green-500",
    cardClass: "border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950",
    accent: "#22c55e",
  },
  CREDITO_CONSUMO: {
    dotClass: "bg-purple-500",
    cardClass: "border-purple-200 bg-purple-50 dark:border-purple-900 dark:bg-purple-950",
    accent: "#a855f7",
  },
  COLEGIO_PENSION: {
    dotClass: "bg-violet-600",
    cardClass: "border-violet-200 bg-violet-50 dark:border-violet-900 dark:bg-violet-950",
    accent: "#7c3aed",
  },
  ADMINISTRACION: {
    dotClass: "bg-orange-500",
    cardClass: "border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-950",
    accent: "#f97316",
  },
  OTRO_SERVICIO: {
    dotClass: "bg-amber-500",
    cardClass: "border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950",
    accent: "#f59e0b",
  },
};

/** Estilo neutro si el backend agrega un tipo que el front todavía no conoce. */
export const FALLBACK_CREDIT_TYPE_STYLE: CreditTypeStyle = {
  dotClass: "bg-gray-400",
  cardClass: "border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900",
  accent: "#9ca3af",
};

export const getCreditTypeStyle = (creditType: string): CreditTypeStyle =>
  CREDIT_TYPE_STYLES[creditType] ?? FALLBACK_CREDIT_TYPE_STYLE;

export const STATUS_META: Record<FinancialPaymentStatus, StatusMeta> = {
  onTime: {
    dotClass: "bg-blue-500",
    chipClass: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
    label: "A tiempo",
    eventColor: "#3b82f6",
    eventTextColor: "#082f49",
  },
  overdue: {
    dotClass: "bg-red-500",
    chipClass: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
    label: "Vencido",
    eventColor: "#ef4444",
    eventTextColor: "#450a0a",
  },
  partialPaid: {
    dotClass: "bg-amber-500",
    chipClass: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
    label: "Pago parcial",
    eventColor: "#f59e0b",
    eventTextColor: "#451a03",
  },
  totalPaid: {
    dotClass: "bg-green-500",
    chipClass: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    label: "Pago total",
    eventColor: "#22c55e",
    eventTextColor: "#052e16",
  },
};
