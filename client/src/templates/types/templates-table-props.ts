import type { Template } from "@/types/templates/template-types";

export interface TemplatesTableProps {
  items: Template[];
  isAdmin: boolean;
  total: number;
  page: number;
  pages: number;
  onPreview: (template: Template) => void;
  onSend: (template: Template) => void;
  onEdit: (template: Template) => void;
  onDelete: (template: Template) => void;
  onPageChange: (page: number) => void;
}
