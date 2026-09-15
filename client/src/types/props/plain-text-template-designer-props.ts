import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

export interface PlainTextTemplateDesignerProps {
  value: string;
  onChange: (value: string) => void;
  maxChars?: number;
  variables: TemplateVariableOption[];
  loadingVariables?: boolean;
}
