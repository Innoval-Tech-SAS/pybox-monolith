import { Card, CardTitle } from "@/ui/components/card";
import { Select } from "@/ui/components/inputs/select";
import { Input } from "@/ui/components/inputs/input";
import { ColumnFields } from "@/databases/components/column-fields";
import { ALTER_ACTION_OPTIONS } from "@/databases/constants/table-wizard-options";
import type { AlterAction } from "@/databases/types/database-types";
import type { StepAlterChangeProps } from "@/databases/types/step-alter-change-props";

export const StepAlterChange: React.FC<StepAlterChangeProps> = ({ form, set, fields }) => {
  const fieldOptions = fields.map((f) => ({ value: f.name, label: `${f.name} (${f.type})` }));

  return (
    <Card className="flex h-full flex-col gap-5">
      <div>
        <CardTitle>Tipo de cambio</CardTitle>
        <Select
          options={ALTER_ACTION_OPTIONS}
          value={form.action}
          onChange={(v) => set("action")(v as AlterAction)}
        />
      </div>

      {form.action === "ADD_COLUMN" && (
        <div>
          <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-400">Nueva columna</p>
          <ColumnFields column={form.addColumn} onChange={(patch) => set("addColumn")({ ...form.addColumn, ...patch })} />
        </div>
      )}

      {form.action === "DROP_COLUMN" && (
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Columna a eliminar</label>
          <Select
            options={fieldOptions}
            value={form.dropColumnName}
            onChange={set("dropColumnName")}
            placeholder="Selecciona una columna"
          />
        </div>
      )}

      {form.action === "MODIFY_COLUMN" && (
        <div className="space-y-3">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Columna a modificar</label>
            <Select
              options={fieldOptions}
              value={form.modifyColumnName}
              onChange={set("modifyColumnName")}
              placeholder="Selecciona una columna"
            />
          </div>
          {form.modifyColumnName && (
            <ColumnFields
              column={form.modifyColumn}
              onChange={(patch) => set("modifyColumn")({ ...form.modifyColumn, ...patch })}
              showConstraints={false}
            />
          )}
        </div>
      )}

      {form.action === "RENAME_COLUMN" && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Columna actual</label>
            <Select
              options={fieldOptions}
              value={form.renameColumnName}
              onChange={set("renameColumnName")}
              placeholder="Selecciona una columna"
            />
          </div>
          <Input
            label="Nuevo nombre *"
            value={form.newColumnName}
            onChange={(e) => set("newColumnName")(e.target.value)}
            placeholder="Ej: fecha_actualizacion"
          />
        </div>
      )}
    </Card>
  );
};
