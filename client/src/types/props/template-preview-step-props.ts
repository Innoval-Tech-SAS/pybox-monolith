import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { TemplateChannel } from "@/types/templates/template-types";

export interface TemplatePreviewStepProps {
  channel: TemplateChannel;
  name: string;
  subject?: string;
  body: string;
  variables: TemplateVariableOption[];
}
