export type CampaignStatus =
  | "BORRADOR"
  | "PROGRAMADA"
  | "EN_EJECUCION"
  | "COMPLETADA"
  | "FALLIDA"
  | "PAUSADA"
  | "CANCELADA";

export type Periodicity = "UNA_VEZ" | "INMEDIATO" | "DIARIO" | "SEMANAL" | "MENSUAL";

export interface Campaign {
  id: string;
  organizationId: string;
  name: string;
  message: string;
  subject?: string | null;
  channelId: string;
  description?: string | null;
  status: CampaignStatus;
  totalRecipients: number;
  scheduledAt?: string | null;
  timezone: string;
  fallback: boolean;
  segmentId?: string | null;
  templateId?: string | null;
  ivrFlowId?: string | null;
  periodicity?: Periodicity | null;
  timeToSend?: string | null;
  isImmediate: boolean;
  daysOfWeek?: number[] | null;
  dayOfMonth?: number | null;
  createdAt: string;
  updatedAt?: string | null;
}

export interface CampaignCreatePayload {
  name: string;
  message: string;
  subject?: string | null;
  channelId: string;
  description?: string | null;
  scheduledAt?: string | null;
  timezone: string;
  fallback: boolean;
  segmentId?: string | null;
  templateId?: string | null;
  ivrFlowId?: string | null;
  periodicity?: Periodicity | null;
  timeToSend?: string | null;
  isImmediate: boolean;
  daysOfWeek?: number[] | null;
  dayOfMonth?: number | null;
}

export interface CampaignUpdatePayload {
  name?: string;
  message?: string;
  subject?: string | null;
  channelId?: string;
  description?: string | null;
  scheduledAt?: string | null;
  timezone?: string;
  fallback?: boolean;
  segmentId?: string | null;
  templateId?: string | null;
  ivrFlowId?: string | null;
  periodicity?: Periodicity | null;
  timeToSend?: string | null;
  isImmediate?: boolean;
  daysOfWeek?: number[] | null;
  dayOfMonth?: number | null;
}

export interface CampaignListResponse {
  items: Campaign[];
  total: number;
  page: number;
  pageSize: number;
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

export interface CampaignOccurrence {
  campaignId: string;
  portfolioId: string;
  campaignName: string;
  occursAt: string;
  periodicity?: Periodicity | null;
  status: CampaignStatus;
  isImmediate: boolean;
}

export interface CampaignTimelineResponse {
  items: CampaignOccurrence[];
  rangeStart: string;
  rangeEnd: string;
}

export interface WeekdayOption {
  value: number;
  label: string;
  active: boolean;
}
