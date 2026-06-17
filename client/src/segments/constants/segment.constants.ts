import type { AggFunction, FilterOp, HavingOp, JoinHow } from "@/segments/types/segment.types";

export const AUDIT_FIELDS = ["fecha_creacion", "fecha_actualizacion", "eliminado_en"];

export const MAIN_TABLES = [
  { name: "deudores", label: "Deudores" },
  { name: "creditos", label: "Créditos" },
];

export const ADDITIONAL_TABLES = [
  { name: "creditos", label: "Créditos" },
  { name: "pagos", label: "Pagos" },
  { name: "metodos_pago", label: "Métodos de pago" },
  { name: "metodos_contacto", label: "Métodos de contacto" },
  { name: "direcciones", label: "Direcciones" },
  { name: "deudores", label: "Deudores" },
];

export const ALL_TABLES = [
  { name: "deudores", label: "Deudores" },
  { name: "creditos", label: "Créditos" },
  { name: "pagos", label: "Pagos" },
  { name: "metodos_pago", label: "Métodos de pago" },
  { name: "metodos_contacto", label: "Métodos de contacto" },
  { name: "direcciones", label: "Direcciones" },
];

export const FILTER_OPS: { value: FilterOp; label: string }[] = [
  { value: "=", label: "= (igual)" },
  { value: "!=", label: "≠ (distinto)" },
  { value: ">", label: "> (mayor)" },
  { value: "<", label: "< (menor)" },
  { value: ">=", label: "≥ (mayor o igual)" },
  { value: "<=", label: "≤ (menor o igual)" },
  { value: "like", label: "like" },
  { value: "ilike", label: "ilike (sin distinción de mayúsculas)" },
  { value: "in", label: "in (lista de valores)" },
  { value: "not_in", label: "not in" },
  { value: "between", label: "between (rango)" },
  { value: "is_null", label: "es nulo" },
  { value: "is_not_null", label: "no es nulo" },
];

export const JOIN_TYPES: { value: JoinHow; label: string }[] = [
  { value: "inner", label: "Inner join" },
  { value: "left", label: "Left join" },
  { value: "right", label: "Right join" },
  { value: "full", label: "Full outer join" },
];

export const OPS_WITHOUT_VALUE: FilterOp[] = ["is_null", "is_not_null"];
export const OPS_WITH_MULTIPLE_VALUES: FilterOp[] = ["in", "not_in", "between"];

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

export const SEGMENT_STEPS = [
  "Información básica",
  "Tablas y filtros",
  "Uniones",
  "Agregación",
  "Resumen",
];
