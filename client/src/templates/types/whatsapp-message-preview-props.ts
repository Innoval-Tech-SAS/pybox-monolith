import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

export interface WhatsAppMessagePreviewProps {
  header: string;
  body: string;
  footer: string;
  variables: TemplateVariableOption[];
}
