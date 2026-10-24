import type { Template } from "@/types/templates/template-types";
import type { WhatsAppTemplateData } from "@/types/templates/whatsapp-template-types";
import type { SortOrder } from "@/ui/components/table/sort-icon";
import type { TemplateSortKey } from "@/templates/hooks/use-templates";

export interface TemplatesTableProps {
  items: Template[];
  isAdmin: boolean;
  loading: boolean;
  total: number;
  page: number;
  pages: number;
  search: string;
  pageSize: number;
  sortKey: TemplateSortKey;
  sortOrder: SortOrder;
  whatsappData: Record<string, WhatsAppTemplateData>;
  refreshingId: string | null;
  onSearch: (q: string) => void;
  onPageSizeChange: (size: number) => void;
  onSort: (key: TemplateSortKey) => void;
  onPreview: (template: Template) => void;
  onSend: (template: Template) => void;
  onEdit: (template: Template) => void;
  onDelete: (template: Template) => void;
  onRefreshStatus: (template: Template) => void;
  onPageChange: (page: number) => void;
}
