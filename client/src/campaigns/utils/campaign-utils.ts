import type { Campaign } from "@/types/campaigns/campaign-types";

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
