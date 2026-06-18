import type { TemplateChannel, TemplateStatus } from "@/types/templates/template-types";

export interface TemplateEditorFormState {
  name: string;
  channel: TemplateChannel;
  status: TemplateStatus;
  body: string;
  design: string | null;
  subject: string;
  senderName: string;
  senderEmail: string;
  replyTo: string;
}
