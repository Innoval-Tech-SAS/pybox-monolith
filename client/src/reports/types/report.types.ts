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

export interface ReportTableFilter {
  column: string;
  op: FilterOp;
  value: string | string[] | null;
}

export interface ReportFormTable {
  name: string;
  alias: string;
  columns: string[];
  filters: ReportTableFilter[];
}

export interface ReportJoin {
  left: string;
  right: string;
  leftOn: string;
  rightOn: string;
  how: JoinHow;
}

export interface ReportGroupBy {
  table: string;
  column: string;
  alias: string;
}

export interface ReportAggregation {
  function: AggFunction;
  table: string;
  column: string;
  alias: string;
}

export interface ReportHaving {
  metric: string;
  op: HavingOp;
  value: string | string[] | null;
}

export interface ReportOrderBy {
  field: string;
  direction: SortDirection;
}

export interface ReportFormState {
  name: string;
  description: string;
  mainTable: string;
  mainTableColumns: string[];
  mainTableFilters: ReportTableFilter[];
  additionalTables: ReportFormTable[];
  joins: ReportJoin[];
  aggregateMode: boolean;
  groupBy: ReportGroupBy[];
  aggregations: ReportAggregation[];
  having: ReportHaving[];
  orderBy: ReportOrderBy[];
}

export interface FieldInfo {
  name: string;
  type: string;
}

// API types

export interface ReportResponse {
  id: string;
  name: string;
  description: string | null;
  reportConfig: Record<string, unknown>;
  organizationId: string;
}

export interface ReportExecuteRequest {
  mode: "preview" | "audit";
  limit?: number;
}

export interface ReportExecuteResponse {
  success: boolean;
  rows: number;
  columns: string[];
  data: Record<string, unknown>[];
  mode: string;
  fileName: string | null;
  filePath: string | null;
}

export interface ReportExecutionResponse {
  id: string;
  reportId: string;
  mode: string;
  fileName: string | null;
  filePath: string | null;
  rows: number;
  columns: string[];
  executedBy: string;
}
