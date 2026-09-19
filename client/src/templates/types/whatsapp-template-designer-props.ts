import type { TemplateVariableOption } from "@/templates/types/template-variable-option";
import type { WhatsAppTemplateFormState } from "@/templates/types/whatsapp-template-form-state";
import type { WhatsAppContentIssues } from "@/templates/utils/whatsapp-template-components";

export interface WhatsAppTemplateDesignerProps {
  form: WhatsAppTemplateFormState;
  issues: WhatsAppContentIssues;
  variables: TemplateVariableOption[];
  loadingVariables: boolean;
  onHeaderChange: (value: string) => void;
  onBodyChange: (value: string) => void;
  onFooterChange: (value: string) => void;
}
