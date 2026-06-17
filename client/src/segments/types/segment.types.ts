export type FilterOp =
  | "="
  | "!="
  | ">"
  | "<"
  | ">="
  | "<="
  | "like"
  | "ilike"
  | "in"
  | "not_in"
  | "between"
  | "is_null"
  | "is_not_null";

export type JoinHow = "inner" | "left" | "right" | "full";

export type AggFunction = "count" | "sum" | "avg" | "min" | "max";

export type HavingOp = "=" | "!=" | ">" | "<" | ">=" | "<=" | "in" | "not_in" | "between";

export type SortDirection = "asc" | "desc";

export interface SegmentTableFilter {
  column: string;
  op: FilterOp;
  value: string | string[] | null;
}

export interface SegmentFormTable {
  name: string;
  alias: string;
  columns: string[];
  filters: SegmentTableFilter[];
}

export interface SegmentJoin {
  left: string;
  right: string;
  leftOn: string;
  rightOn: string;
  how: JoinHow;
}

export interface SegmentGroupBy {
  table: string;
  column: string;
  alias: string;
}

export interface SegmentAggregation {
  function: AggFunction;
  table: string;
  column: string;
  alias: string;
}

export interface SegmentHaving {
  metric: string;
  op: HavingOp;
  value: string | string[] | null;
}

export interface SegmentOrderBy {
  field: string;
  direction: SortDirection;
}

export interface SegmentFormState {
  name: string;
  description: string;
  mainTable: string;
  mainTableColumns: string[];
  mainTableFilters: SegmentTableFilter[];
  additionalTables: SegmentFormTable[];
  joins: SegmentJoin[];
  aggregateMode: boolean;
  groupBy: SegmentGroupBy[];
  aggregations: SegmentAggregation[];
  having: SegmentHaving[];
  orderBy: SegmentOrderBy[];
}

export interface FieldInfo {
  name: string;
  type: string;
}

// API types

export interface SegmentResponse {
  id: string;
  name: string;
  description: string | null;
  filterCriteria: Record<string, unknown>;
  organizationId: string;
}

export interface SegmentExecuteRequest {
  mode: "preview" | "audit";
  limit?: number;
}

export interface SegmentExecuteResponse {
  success: boolean;
  rows: number;
  columns: string[];
  data: Record<string, unknown>[];
  mode: string;
  fileName: string | null;
  filePath: string | null;
}

export interface SegmentExecutionResponse {
  id: string;
  segmentId: string;
  mode: string;
  fileName: string | null;
  filePath: string | null;
  rows: number;
  columns: string[];
  executedBy: string;
}
