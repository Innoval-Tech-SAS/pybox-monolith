export type CampaignStatus =
  | "borrador"
  | "programada"
  | "en ejecución"
  | "completada"
  | "fallida"
  | "pausada"
  | "cancelada";

export type Periodicity = "once" | "immediate" | "daily" | "weekly" | "monthly";

export type CampaignChannel = "SMS" | "EMAIL" | "WHATSAPP" | "CALL";

export interface Campaign {
  id: string;
  organizationId: string;
  name: string;
  message: string;
  subject?: string | null;
  channel: string;
  description?: string | null;
  status: CampaignStatus;
  totalRecipients: number;
  scheduledAt?: string | null;
  timezone: string;
  fallback: boolean;
  segmentId?: string | null;
  templateId?: string | null;
  periodicity?: Periodicity | null;
  timeToSend?: string | null;
  isImmediate: boolean;
  daysOfWeek?: number[] | null;
  createdAt: string;
  updatedAt?: string | null;
}

export interface CampaignCreatePayload {
  name: string;
  message: string;
  subject?: string | null;
  channel: string;
  description?: string | null;
  scheduledAt?: string | null;
  timezone: string;
  fallback: boolean;
  segmentId?: string | null;
  templateId?: string | null;
  periodicity?: Periodicity | null;
  timeToSend?: string | null;
  isImmediate: boolean;
  daysOfWeek?: number[] | null;
}

export interface CampaignUpdatePayload {
  name?: string;
  message?: string;
  subject?: string | null;
  channel?: string;
  description?: string | null;
  scheduledAt?: string | null;
  timezone?: string;
  fallback?: boolean;
  segmentId?: string | null;
  templateId?: string | null;
  periodicity?: Periodicity | null;
  timeToSend?: string | null;
  isImmediate?: boolean;
  daysOfWeek?: number[] | null;
}

export interface CampaignStatusResponse {
  campaignId: string;
  status: CampaignStatus;
  isExecuting: boolean;
}

export interface PeriodicityOption {
  value: Periodicity;
  label: string;
}

export interface WeekdayOption {
  value: number;
  label: string;
  active: boolean;
}
