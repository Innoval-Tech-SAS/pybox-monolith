export type ColumnDataType =
  | "TEXT"
  | "VARCHAR"
  | "CHAR"
  | "INTEGER"
  | "BIGINT"
  | "SMALLINT"
  | "NUMERIC"
  | "FLOAT"
  | "DOUBLE PRECISION"
  | "BOOLEAN"
  | "DATE"
  | "TIMESTAMP"
  | "TIMESTAMPTZ"
  | "UUID"
  | "JSONB"
  | "JSON";

export type AlterAction = "ADD_COLUMN" | "DROP_COLUMN" | "MODIFY_COLUMN" | "RENAME_COLUMN";

export interface ColumnDefinition {
  name: string;
  dataType: ColumnDataType;
  nullable: boolean;
  defaultValue: string | null;
  length: number;
  precision: number;
  scale: number;
  primaryKey: boolean;
  unique: boolean;
}

export interface FieldInfo {
  name: string;
  type: string;
}

export interface OperationResponse {
  success: boolean;
  message: string;
}
