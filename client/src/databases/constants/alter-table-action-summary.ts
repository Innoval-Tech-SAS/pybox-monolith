import type { AlterTableFormState } from "@/databases/types/alter-table-form-state";

export const ALTER_TABLE_ACTION_SUMMARY: Record<AlterTableFormState["action"], (form: AlterTableFormState) => string> = {
  ADD_COLUMN: (f) => `Se agregará la columna "${f.addColumn.name}" (${f.addColumn.dataType}) a ${f.schema}.${f.table}.`,
  DROP_COLUMN: (f) => `Se eliminará la columna "${f.dropColumnName}" de ${f.schema}.${f.table}.`,
  MODIFY_COLUMN: (f) => `Se modificará la columna "${f.modifyColumnName}" en ${f.schema}.${f.table} a tipo ${f.modifyColumn.dataType}.`,
  RENAME_COLUMN: (f) => `Se renombrará la columna "${f.renameColumnName}" a "${f.newColumnName}" en ${f.schema}.${f.table}.`,
};
