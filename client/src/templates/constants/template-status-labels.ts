import type { TemplateStatus } from "@/types/templates/template-types";
import type { BadgeColor } from "@/types/props/badge-props";

export const TEMPLATE_STATUS_LABELS: Record<TemplateStatus, string> = {
  BORRADOR: "Borrador",
  ACTIVA: "Activa",
  INACTIVA: "Inactiva",
};

// Colores semánticos de <Badge> -- Fase 9 de la auditoría (antes clases Tailwind
// armadas a mano, fuera del sistema de badges compartido).
export const TEMPLATE_STATUS_COLORS: Record<TemplateStatus, BadgeColor> = {
  BORRADOR: "light",
  ACTIVA: "success",
  INACTIVA: "error",
};
