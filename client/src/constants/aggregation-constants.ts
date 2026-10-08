import type { AggFunction, HavingOp } from "@/types/aggregation-types";

export const AGG_FUNCTIONS: { value: AggFunction; label: string }[] = [
  { value: "count", label: "Contar (COUNT)" },
  { value: "sum", label: "Sumar (SUM)" },
  { value: "avg", label: "Promediar (AVG)" },
  { value: "min", label: "Mínimo (MIN)" },
  { value: "max", label: "Máximo (MAX)" },
];

export const HAVING_OPS: { value: HavingOp; label: string }[] = [
  { value: "=", label: "= (igual)" },
  { value: "!=", label: "≠ (distinto)" },
  { value: ">", label: "> (mayor)" },
  { value: "<", label: "< (menor)" },
  { value: ">=", label: "≥ (mayor o igual)" },
  { value: "<=", label: "≤ (menor o igual)" },
  { value: "in", label: "in (lista de valores)" },
  { value: "not_in", label: "not in" },
  { value: "between", label: "between (rango)" },
];

export const HAVING_OPS_WITH_MULTIPLE_VALUES: HavingOp[] = ["in", "not_in", "between"];
