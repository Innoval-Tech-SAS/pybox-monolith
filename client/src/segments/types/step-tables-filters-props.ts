import type {
  SegmentFormState,
  SegmentFormTable,
  SegmentTableFilter,
  FilterOp,
} from "@/segments/types/segment.types";

export interface StepTablesFiltersProps {
  state: SegmentFormState;
  update: (patch: Partial<SegmentFormState>) => void;
  addTable: (table: SegmentFormTable) => void;
  removeTable: (alias: string) => void;
  updateTable: (alias: string, patch: Partial<SegmentFormTable>) => void;
}

export interface TableSectionProps {
  title: string;
  tableName: string;
  columns: string[];
  filters: SegmentTableFilter[];
  onColumnsChange: (cols: string[]) => void;
  onFiltersChange: (filters: SegmentTableFilter[]) => void;
  removable: boolean;
  onRemove?: () => void;
}

export interface FilterRowProps {
  filter: SegmentTableFilter;
  fields: string[];
  onChange: (patch: Partial<SegmentTableFilter>) => void;
  onRemove: () => void;
}
