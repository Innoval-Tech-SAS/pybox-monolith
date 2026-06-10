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
  | "is_null"
  | "is_not_null";

export type JoinHow = "inner" | "left" | "right" | "full";

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

export interface SegmentFormState {
  name: string;
  description: string;
  mainTable: string;
  mainTableColumns: string[];
  mainTableFilters: SegmentTableFilter[];
  additionalTables: SegmentFormTable[];
  joins: SegmentJoin[];
}

export interface FieldInfo {
  name: string;
  type: string;
}

// API types

export interface SegmentResponse {
  id: number;
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
  id: number;
  segmentId: number;
  mode: string;
  fileName: string | null;
  filePath: string | null;
  rows: number;
  columns: string[];
  executedBy: number;
}
