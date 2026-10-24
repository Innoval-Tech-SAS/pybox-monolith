import type { CampaignStatus } from "@/types/campaigns/campaign-types";
import type { BadgeColor } from "@/types/props/badge-props";

export const CAMPAIGN_STATUS_LABELS: Record<CampaignStatus, string> = {
  "BORRADOR": "Borrador",
  "PROGRAMADA": "Programada",
  "EN_EJECUCION": "En ejecución",
  "COMPLETADA": "Completada",
  "FALLIDA": "Fallida",
  "PAUSADA": "Pausada",
  "CANCELADA": "Cancelada",
};

// Colores semánticos de <Badge> (ui/components/badge.tsx) -- Fase 9 de la auditoría:
// antes eran clases Tailwind armadas a mano, fuera del sistema de badges compartido.
export const CAMPAIGN_STATUS_COLORS: Record<CampaignStatus, BadgeColor> = {
  "BORRADOR": "light",
  "PROGRAMADA": "primary",
  "EN_EJECUCION": "warning",
  "COMPLETADA": "success",
  "FALLIDA": "error",
  "PAUSADA": "info",
  "CANCELADA": "dark",
};
