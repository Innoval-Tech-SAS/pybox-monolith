import type { AlterAction, ColumnDefinition } from "@/databases/types/database-types";

export interface AlterTableFormState {
  schema: string;
  table: string;
  action: AlterAction;
  addColumn: ColumnDefinition;
  dropColumnName: string;
  modifyColumnName: string;
  modifyColumn: ColumnDefinition;
  renameColumnName: string;
  newColumnName: string;
}
