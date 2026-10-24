import type {
  Campaign,
  CampaignOccurrence,
} from "@/types/campaigns/campaign-types";
import type {
  CampaignEditorFormState,
  CampaignFrequency,
  RecurringPeriodicity,
} from "@/campaigns/types/campaign-editor-form-state";
import { CAMPAIGN_STATUS_META } from "@/campaigns/constants/campaign-calendar-meta";
import type { EventInput } from "@fullcalendar/core";

const PERIODICITY_LABELS: Record<string, string> = { DIARIO: "Diaria", SEMANAL: "Semanal", MENSUAL: "Mensual" };
const DAY_LABELS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

export const formatSchedule = (campaign: Campaign): string => {
  if (campaign.isImmediate) return "Inmediato";
  if (campaign.periodicity === "UNA_VEZ") {
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
      campaign.periodicity === "SEMANAL" && campaign.daysOfWeek?.length
        ? ` (${campaign.daysOfWeek.map((d) => DAY_LABELS[d]).join(", ")})`
        : "";
    return `${PERIODICITY_LABELS[campaign.periodicity] ?? campaign.periodicity} · ${campaign.timeToSend.slice(0, 5)}${days}`;
  }
  return "—";
};

export const formatCampaignDateTime = (value: string): string =>
  new Date(value).toLocaleString("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

export const buildCalendarEvents = (occurrences: CampaignOccurrence[]): EventInput[] =>
  occurrences.map((o, idx) => {
    const meta = CAMPAIGN_STATUS_META[o.status];
    return {
      id: `${o.campaignId}-${o.occursAt}-${idx}`,
      title: o.campaignName,
      start: o.occursAt,
      color: meta.eventColor,
      textColor: meta.eventTextColor,
      extendedProps: { occurrence: o },
    };
  });

export const buildCampaignEditorForm = (c: Campaign): CampaignEditorFormState => {
  const frequency: CampaignFrequency = c.isImmediate
    ? "INMEDIATO"
    : c.periodicity === "UNA_VEZ"
      ? "UNA_VEZ"
      : "PERIODICO";
  const recurringPeriodicity: RecurringPeriodicity =
    c.periodicity === "DIARIO" || c.periodicity === "SEMANAL" || c.periodicity === "MENSUAL"
      ? c.periodicity
      : "SEMANAL";
  return {
    name: c.name,
    description: c.description ?? "",
    channelId: c.channelId,
    segmentId: c.segmentId ?? "",
    templateId: c.templateId ?? "",
    ivrFlowId: c.ivrFlowId ?? "",
    message: c.message,
    subject: c.subject ?? "",
    fallback: c.fallback,
    timezone: c.timezone,
    frequency,
    recurringPeriodicity,
    scheduledAt: c.scheduledAt ? c.scheduledAt.slice(0, 16) : "",
    timeToSend: c.timeToSend ? c.timeToSend.slice(0, 5) : "",
    daysOfWeek: c.daysOfWeek ?? [],
    dayOfMonth: c.dayOfMonth ?? null,
  };
};

export const isCampaignScheduleValid = (form: CampaignEditorFormState): boolean =>
  form.frequency === "INMEDIATO"
    ? true
    : form.frequency === "UNA_VEZ"
      ? !!form.scheduledAt
      : !!form.recurringPeriodicity &&
        !!form.timeToSend &&
        (form.recurringPeriodicity !== "SEMANAL" || form.daysOfWeek.length > 0) &&
        (form.recurringPeriodicity !== "MENSUAL" || !!form.dayOfMonth);
