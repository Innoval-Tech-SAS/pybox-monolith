import type { BadgeColor } from "@/types/props/badge-props";

/**
 * Punto de color por prioridad judicial. Solo estilo: el código y la etiqueta legible
 * los sirve el backend (`GET /judicial-notifications/priorities`).
 *
 * Las claves son los códigos del enum `JudicialPriority`.
 */
export const JUDICIAL_PRIORITY_DOT: Record<string, string> = {
  URGENTE: "bg-error-500",
  MEDIA: "bg-orange-500",
  BAJA: "bg-amber-400",
  INFORMATIVA: "bg-success-500",
};

/** Mismo mapeo que `JUDICIAL_PRIORITY_DOT`, pero para el color de `Badge`. */
export const JUDICIAL_PRIORITY_BADGE_COLOR: Record<string, BadgeColor> = {
  URGENTE: "error",
  MEDIA: "warning",
  BAJA: "warning",
  INFORMATIVA: "success",
};
