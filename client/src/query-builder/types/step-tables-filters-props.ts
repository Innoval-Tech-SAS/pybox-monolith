import type { EntityFormState, FormTable, TableFilter, FieldInfo } from "@/query-builder/types/query-builder-types";
import type { QueryBuilderEntityConfig } from "@/query-builder/types/query-builder-entity-config";

export interface StepTablesFiltersProps {
  state: EntityFormState;
  update: (patch: Partial<EntityFormState>) => void;
  addTable: (table: FormTable) => void;
  removeTable: (alias: string) => void;
  updateTable: (alias: string, patch: Partial<FormTable>) => void;
  config: QueryBuilderEntityConfig;
}

export interface TableSectionProps {
  title: string;
  tableName: string;
  columns: string[];
  filters: TableFilter[];
  onColumnsChange: (cols: string[]) => void;
  onFiltersChange: (filters: TableFilter[]) => void;
  removable: boolean;
  onRemove?: () => void;
}

export interface FilterRowProps {
  filter: TableFilter;
  fields: FieldInfo[];
  onChange: (patch: Partial<TableFilter>) => void;
  onRemove: () => void;
}
