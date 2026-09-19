import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

export interface TemplateEditorProps {
  value: string;
  design?: string | null;
  onChange: (html: string, design: string) => void;
  variables?: TemplateVariableOption[];
  loadingVariables?: boolean;
}
