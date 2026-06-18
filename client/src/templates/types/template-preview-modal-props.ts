import type { Template, TemplatePreviewResponse } from "@/types/templates/template-types";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

export interface TemplatePreviewModalProps {
  isOpen: boolean;
  template: Template | null;
  variableOptions: TemplateVariableOption[];
  onClose: () => void;
  onPreview: (id: string, sub: Record<string, string>) => Promise<TemplatePreviewResponse | null>;
}
