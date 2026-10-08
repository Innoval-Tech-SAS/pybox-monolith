import type { SelectOption } from "@/types/props/select-props";
import type { ColumnDataType, ColumnDefinition } from "@/databases/types/database-types";

export const COLUMN_DATA_TYPE_OPTIONS: SelectOption[] = [
  { value: "TEXT", label: "TEXT" },
  { value: "VARCHAR", label: "VARCHAR" },
  { value: "CHAR", label: "CHAR" },
  { value: "INTEGER", label: "INTEGER" },
  { value: "BIGINT", label: "BIGINT" },
  { value: "SMALLINT", label: "SMALLINT" },
  { value: "NUMERIC", label: "NUMERIC" },
  { value: "FLOAT", label: "FLOAT" },
  { value: "DOUBLE PRECISION", label: "DOUBLE PRECISION" },
  { value: "BOOLEAN", label: "BOOLEAN" },
  { value: "DATE", label: "DATE" },
  { value: "TIMESTAMP", label: "TIMESTAMP" },
  { value: "TIMESTAMPTZ", label: "TIMESTAMPTZ" },
  { value: "UUID", label: "UUID" },
  { value: "JSONB", label: "JSONB" },
  { value: "JSON", label: "JSON" },
];

// Tipos que aceptan longitud/precisión/escala en su definición SQL.
export const LENGTH_DATA_TYPES: ColumnDataType[] = ["VARCHAR", "CHAR"];
export const PRECISION_DATA_TYPES: ColumnDataType[] = ["NUMERIC"];

export const emptyColumnDefinition = (): ColumnDefinition => ({
  name: "",
  dataType: "TEXT",
  nullable: true,
  defaultValue: "",
  length: 0,
  precision: 0,
  scale: 0,
  primaryKey: false,
  unique: false,
});
