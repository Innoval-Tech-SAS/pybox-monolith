// Tipos compartidos por el wizard de agregaciones de segments y reports
// (ambos backends exponen el mismo contrato de agrupación/agregación/having/orden).

export type AggFunction = "count" | "sum" | "avg" | "min" | "max";

export type HavingOp = "=" | "!=" | ">" | "<" | ">=" | "<=" | "in" | "not_in" | "between";

export type SortDirection = "asc" | "desc";

export interface AggregationTableRef {
  alias: string;
  name: string;
}

export interface AggregationGroupBy {
  table: string;
  column: string;
  alias: string;
}

export interface AggregationMetric {
  function: AggFunction;
  table: string;
  column: string;
  alias: string;
}

export interface AggregationHaving {
  metric: string;
  op: HavingOp;
  value: string | string[] | null;
}

export interface AggregationOrderBy {
  field: string;
  direction: SortDirection;
}

// Slice de estado del formulario que el wizard de agregación necesita leer/escribir;
// EntityFormState (query-builder/) lo satisface estructuralmente.
export interface AggregationStepState {
  mainTable: string;
  additionalTables: AggregationTableRef[];
  aggregateMode: boolean;
  groupBy: AggregationGroupBy[];
  aggregations: AggregationMetric[];
  having: AggregationHaving[];
  orderBy: AggregationOrderBy[];
}
