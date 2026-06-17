import type {
  ReportAggregation,
  ReportFormState,
  ReportGroupBy,
  ReportHaving,
  ReportOrderBy,
} from "@/reports/types/report.types";

export interface StepAggregationProps {
  state: ReportFormState;
  update: (patch: Partial<ReportFormState>) => void;
}

export interface ReportTableRef {
  alias: string;
  name: string;
}

export interface GroupByRowProps {
  group: ReportGroupBy;
  tables: ReportTableRef[];
  onChange: (patch: Partial<ReportGroupBy>) => void;
  onRemove: () => void;
}

export interface AggregationRowProps {
  aggregation: ReportAggregation;
  tables: ReportTableRef[];
  onChange: (patch: Partial<ReportAggregation>) => void;
  onRemove: () => void;
}

export interface HavingRowProps {
  having: ReportHaving;
  metricOptions: string[];
  onChange: (patch: Partial<ReportHaving>) => void;
  onRemove: () => void;
}

export interface OrderByRowProps {
  order: ReportOrderBy;
  fieldOptions: string[];
  onChange: (patch: Partial<ReportOrderBy>) => void;
  onRemove: () => void;
}
