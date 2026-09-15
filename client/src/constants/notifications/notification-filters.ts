import type { NotifType } from "@/types/notifications/notification";

export const TYPE_LABELS: Record<NotifType, string> = {
  success: "Completadas",
  info: "Información",
  warning: "Advertencias",
  error: "Errores",
};

export const FILTERS = [
  { key: "all", label: "Todas" },
  { key: "success", label: "Completadas" },
  { key: "info", label: "Información" },
  { key: "warning", label: "Advertencias" },
  { key: "error", label: "Errores" },
] as const;

export type FilterKey = (typeof FILTERS)[number]["key"];
