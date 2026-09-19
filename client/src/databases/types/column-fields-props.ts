import type { ColumnDefinition } from "@/databases/types/database-types";

export interface ColumnFieldsProps {
  column: ColumnDefinition;
  onChange: (patch: Partial<ColumnDefinition>) => void;
  onRemove?: () => void;
  showConstraints?: boolean;
}

export interface ColumnListEditorProps {
  columns: ColumnDefinition[];
  onChange: (columns: ColumnDefinition[]) => void;
}
