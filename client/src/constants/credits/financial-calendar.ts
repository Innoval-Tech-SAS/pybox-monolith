import type { FinancialPaymentStatus, StatusMeta } from "@/credits/types/financial-calendar-types";

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
