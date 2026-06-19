export type CampaignFrequency = "immediate" | "once" | "periodic";
export type RecurringPeriodicity = "daily" | "weekly" | "monthly";

export interface CampaignEditorFormState {
  name: string;
  description: string;
  channelId: string;
  segmentId: string;
  templateId: string;
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
