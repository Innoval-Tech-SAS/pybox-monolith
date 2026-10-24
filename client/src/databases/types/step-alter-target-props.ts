import type { AlterTableFormState } from "@/databases/types/alter-table-form-state";

export interface StepAlterTargetProps {
  form: AlterTableFormState;
  set: <K extends keyof AlterTableFormState>(key: K) => (value: AlterTableFormState[K]) => void;
  schemas: string[];
  tables: string[];
}
