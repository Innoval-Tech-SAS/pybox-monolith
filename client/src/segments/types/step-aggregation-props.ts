import type {
  SegmentAggregation,
  SegmentFormState,
  SegmentGroupBy,
  SegmentHaving,
  SegmentOrderBy,
} from "@/segments/types/segment.types";

export interface StepAggregationProps {
  state: SegmentFormState;
  update: (patch: Partial<SegmentFormState>) => void;
}

export interface SegmentTableRef {
  alias: string;
  name: string;
}

export interface GroupByRowProps {
  group: SegmentGroupBy;
  tables: SegmentTableRef[];
  onChange: (patch: Partial<SegmentGroupBy>) => void;
  onRemove: () => void;
}

export interface AggregationRowProps {
  aggregation: SegmentAggregation;
  tables: SegmentTableRef[];
  onChange: (patch: Partial<SegmentAggregation>) => void;
  onRemove: () => void;
}

export interface HavingRowProps {
  having: SegmentHaving;
  metricOptions: string[];
  onChange: (patch: Partial<SegmentHaving>) => void;
  onRemove: () => void;
}

export interface OrderByRowProps {
  order: SegmentOrderBy;
  fieldOptions: string[];
  onChange: (patch: Partial<SegmentOrderBy>) => void;
  onRemove: () => void;
}
