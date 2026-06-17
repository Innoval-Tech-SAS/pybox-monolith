import type {
  ReportFormState,
  ReportFormTable,
  ReportTableFilter,
  FieldInfo,
} from "@/reports/types/report.types";

export interface StepTablesFiltersProps {
  state: ReportFormState;
  update: (patch: Partial<ReportFormState>) => void;
  addTable: (table: ReportFormTable) => void;
  removeTable: (alias: string) => void;
  updateTable: (alias: string, patch: Partial<ReportFormTable>) => void;
}

export interface TableSectionProps {
  title: string;
  tableName: string;
  columns: string[];
  filters: ReportTableFilter[];
  onColumnsChange: (cols: string[]) => void;
  onFiltersChange: (filters: ReportTableFilter[]) => void;
  removable: boolean;
  onRemove?: () => void;
}

export interface FilterRowProps {
  filter: ReportTableFilter;
  fields: FieldInfo[];
  onChange: (patch: Partial<ReportTableFilter>) => void;
  onRemove: () => void;
}
