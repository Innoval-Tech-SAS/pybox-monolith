export type TemplateChannel = "EMAIL" | "SMS";
export type TemplateStatus = "DRAFT" | "ACTIVE" | "INACTIVE";

export interface Template {
  id: string;
  organizationId: string;
  name: string;
  channel: TemplateChannel;
  status: TemplateStatus;
  body: string;
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
  subject?: string | null;
  senderName?: string | null;
  senderEmail?: string | null;
  replyTo?: string | null;
}

export interface TemplateUpdatePayload {
  name?: string;
  status?: TemplateStatus;
  body?: string;
  subject?: string | null;
  senderName?: string | null;
  senderEmail?: string | null;
  replyTo?: string | null;
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
