import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { WhatsAppTemplateFormState } from "@/templates/types/whatsapp-template-form-state";

export interface StepWhatsAppPreviewProps {
  name: string;
  whatsappForm: WhatsAppTemplateFormState;
  variables: TemplateVariableOption[];
}
