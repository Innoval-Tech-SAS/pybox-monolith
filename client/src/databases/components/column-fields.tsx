import { Trash2 } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { Switch } from "@/ui/components/switch";
import {
  COLUMN_DATA_TYPE_OPTIONS,
  LENGTH_DATA_TYPES,
  PRECISION_DATA_TYPES,
} from "@/databases/constants/column-data-type-options";
import type { ColumnDataType } from "@/databases/types/database-types";
import type { ColumnFieldsProps } from "@/databases/types/column-fields-props";

export const ColumnFields: React.FC<ColumnFieldsProps> = ({ column, onChange, onRemove, showConstraints = true }) => {
  const showsLength = LENGTH_DATA_TYPES.includes(column.dataType);
  const showsPrecision = PRECISION_DATA_TYPES.includes(column.dataType);

  return (
    <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-white/3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Input
          label="Nombre *"
          value={column.name}
          onChange={(e) => onChange({ name: e.target.value })}
          placeholder="Ej: fecha_pago"
        />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Tipo de dato</label>
          <Select
            options={COLUMN_DATA_TYPE_OPTIONS}
            value={column.dataType}
            onChange={(v) => onChange({ dataType: v as ColumnDataType })}
          />
        </div>

        {showsLength && (
          <Input
            type="number"
            label="Longitud"
            value={String(column.length)}
            onChange={(e) => onChange({ length: Number(e.target.value) || 0 })}
            placeholder="Ej: 255"
          />
        )}

        {showsPrecision && (
          <>
            <Input
              type="number"
              label="Precisión"
              value={String(column.precision)}
              onChange={(e) => onChange({ precision: Number(e.target.value) || 0 })}
              placeholder="Ej: 10"
            />
            <Input
              type="number"
              label="Escala"
              value={String(column.scale)}
              onChange={(e) => onChange({ scale: Number(e.target.value) || 0 })}
              placeholder="Ej: 2"
            />
          </>
        )}

        <Input
          label="Valor por defecto"
          value={column.defaultValue ?? ""}
          onChange={(e) => onChange({ defaultValue: e.target.value })}
          placeholder="Ej: NOW(), 0, 'activo'…"
        />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-5">
        <Switch checked={column.nullable} onChange={(v) => onChange({ nullable: v })} label="Acepta nulos" />

        {showConstraints && (
          <>
            <Switch
              checked={column.primaryKey}
              onChange={(v) => onChange({ primaryKey: v, nullable: v ? false : column.nullable })}
              label="Llave primaria"
            />
            <Switch checked={column.unique} onChange={(v) => onChange({ unique: v })} label="Único" />
          </>
        )}

        {onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="ml-auto flex items-center gap-1.5 rounded p-1.5 text-gray-400 hover:text-red-500"
          >
            <Trash2 size={15} />
          </button>
        )}
      </div>
    </div>
  );
};
