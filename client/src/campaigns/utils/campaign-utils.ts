import type { Campaign, CampaignStatus } from "@/types/campaigns/campaign-types";

export const STATUS_LABELS: Record<CampaignStatus, string> = {
  "borrador": "Borrador",
  "programada": "Programada",
  "en ejecución": "En ejecución",
  "completada": "Completada",
  "fallida": "Fallida",
  "pausada": "Pausada",
  "cancelada": "Cancelada",
};

export const STATUS_COLORS: Record<CampaignStatus, string> = {
  "borrador": "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  "programada": "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-400",
  "en ejecución": "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-orange-400",
  "completada": "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  "fallida": "bg-error-50 text-error-600 dark:bg-error-500/10 dark:text-error-400",
  "pausada": "bg-orange-50 text-orange-700 dark:bg-orange-500/15 dark:text-orange-400",
  "cancelada": "bg-gray-200 text-gray-600 dark:bg-white/5 dark:text-gray-500",
};

const PERIODICITY_LABELS: Record<string, string> = { daily: "Diaria", weekly: "Semanal", monthly: "Mensual" };
const DAY_LABELS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

export const formatSchedule = (campaign: Campaign): string => {
  if (campaign.isImmediate) return "Inmediato";
  if (campaign.periodicity === "once") {
    return campaign.scheduledAt
      ? new Date(campaign.scheduledAt).toLocaleString("es-CO", {
          day: "2-digit",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })
      : "—";
  }
  if (campaign.periodicity && campaign.timeToSend) {
    const days =
      campaign.periodicity === "weekly" && campaign.daysOfWeek?.length
        ? ` (${campaign.daysOfWeek.map((d) => DAY_LABELS[d]).join(", ")})`
        : "";
    return `${PERIODICITY_LABELS[campaign.periodicity] ?? campaign.periodicity} · ${campaign.timeToSend.slice(0, 5)}${days}`;
  }
  return "—";
};
