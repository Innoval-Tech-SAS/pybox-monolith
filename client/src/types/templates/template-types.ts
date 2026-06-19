import type { ChannelName } from "@/types/channels/channel-types";

export type TemplateChannel = ChannelName;
export type TemplateStatus = "DRAFT" | "ACTIVE" | "INACTIVE";

export interface Template {
  id: string;
  organizationId: string;
  name: string;
  channel: TemplateChannel;
  status: TemplateStatus;
  body: string;
  design?: string | null;
  subject?: string | null;
  senderName?: string | null;
  senderEmail?: string | null;
  replyTo?: string | null;
  createdAt: string;
  updatedAt?: string | null;
}

export interface TemplateCreatePayload {
  name: string;
  channel: TemplateChannel;
  status?: TemplateStatus;
  body: string;
  design?: string | null;
  subject?: string | null;
  senderName?: string | null;
  senderEmail?: string | null;
  replyTo?: string | null;
}

export interface TemplateUpdatePayload {
  name?: string;
  status?: TemplateStatus;
  body?: string;
  design?: string | null;
  subject?: string | null;
  senderName?: string | null;
  senderEmail?: string | null;
  replyTo?: string | null;
}

export interface TemplateListResponse {
  items: Template[];
  total: number;
  page: number;
  pageSize: number;
}

export interface TemplatePreviewRequest {
  sub: Record<string, string>;
}

export interface TemplatePreviewResponse {
  html: string;
  subject: string;
  variablesUsed: string[];
}

export interface TemplateSendRequest {
  to: string;
  subject?: string | null;
  sub: Record<string, string>;
}

export interface TemplateSendResponse {
  message: string;
}
