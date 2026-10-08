import { Card, CardTitle } from "@/ui/components/card";
import { Select } from "@/ui/components/inputs/select";
import type { StepAlterTargetProps } from "@/databases/types/step-alter-target-props";

export const StepAlterTarget: React.FC<StepAlterTargetProps> = ({ form, set, schemas, tables }) => (
  <Card className="flex h-full flex-col">
    <CardTitle>Selecciona la tabla a modificar</CardTitle>
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Esquema</label>
        <Select
          options={schemas.map((s) => ({ value: s, label: s }))}
          value={form.schema}
          onChange={(v) => { set("schema")(v); set("table")(""); }}
        />
      </div>
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Tabla</label>
        <Select
          options={tables.map((t) => ({ value: t, label: t }))}
          value={form.table}
          onChange={set("table")}
          placeholder="Selecciona una tabla"
        />
      </div>
    </div>
  </Card>
);
