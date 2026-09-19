import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

export interface StepDesignProps {
  isEmail: boolean;
  isUnavailable: boolean;
  body: string;
  design: string | null;
  onBodyChange: (value: string) => void;
  onDesignChange: (html: string, design: string) => void;
  charLimit?: number;
  variables: TemplateVariableOption[];
  loadingVariables: boolean;
}
