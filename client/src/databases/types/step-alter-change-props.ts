import type { AlterTableFormState } from "@/databases/types/alter-table-form-state";
import type { FieldInfo } from "@/databases/types/database-types";

export interface StepAlterChangeProps {
  form: AlterTableFormState;
  set: <K extends keyof AlterTableFormState>(key: K) => (value: AlterTableFormState[K]) => void;
  fields: FieldInfo[];
}
