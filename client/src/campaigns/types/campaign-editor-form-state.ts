export type CampaignFrequency = "INMEDIATO" | "UNA_VEZ" | "PERIODICO";
export type RecurringPeriodicity = "DIARIO" | "SEMANAL" | "MENSUAL";

export interface CampaignEditorFormState {
  name: string;
  description: string;
  channelId: string;
  segmentId: string;
  templateId: string;
  /** Flujo IVR seleccionado (canal CALL). */
  ivrFlowId: string;
  message: string;
  subject: string;
  fallback: boolean;
  timezone: string;
  frequency: CampaignFrequency;
  recurringPeriodicity: RecurringPeriodicity;
  scheduledAt: string;
  timeToSend: string;
  daysOfWeek: number[];
  dayOfMonth: number | null;
}
