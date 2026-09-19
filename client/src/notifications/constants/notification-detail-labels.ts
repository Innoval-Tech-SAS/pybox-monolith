import type { NotifType } from "@/types/notifications/notification";

export const NOTIF_TYPE_BADGES: Record<NotifType, { label: string; className: string }> = {
  success: { label: "Completado", className: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400" },
  info: { label: "Información", className: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400" },
  warning: { label: "Advertencia", className: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400" },
  error: { label: "Error", className: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400" },
};

export const NOTIF_DETAIL_LABELS: Record<string, string> = {
  creditos: "Créditos",
  titulares: "Titulares",
  codeudores: "Codeudores",
  clientes_unicos: "Clientes únicos",
};
