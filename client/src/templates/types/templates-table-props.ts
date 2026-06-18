import type { Template } from "@/types/templates/template-types";

export interface TemplatesTableProps {
  items: Template[];
  isAdmin: boolean;
  onPreview: (template: Template) => void;
  onSend: (template: Template) => void;
  onEdit: (template: Template) => void;
  onDelete: (template: Template) => void;
}
