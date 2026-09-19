import { Plus } from "lucide-react";
import { ColumnFields } from "@/databases/components/column-fields";
import { emptyColumnDefinition } from "@/databases/constants/column-data-type-options";
import type { ColumnListEditorProps } from "@/databases/types/column-fields-props";

export const ColumnListEditor: React.FC<ColumnListEditorProps> = ({ columns, onChange }) => {
  const updateColumn = (index: number, patch: Partial<(typeof columns)[number]>) => {
    onChange(columns.map((c, i) => (i === index ? { ...c, ...patch } : c)));
  };

  const removeColumn = (index: number) => {
    onChange(columns.filter((_, i) => i !== index));
  };

  const addColumn = () => {
    onChange([...columns, emptyColumnDefinition()]);
  };

  return (
    <div className="space-y-3">
      {columns.length === 0 ? (
        <p className="text-xs text-gray-400 dark:text-gray-500">Sin columnas definidas.</p>
      ) : (
        columns.map((column, i) => (
          <ColumnFields
            key={i}
            column={column}
            onChange={(patch) => updateColumn(i, patch)}
            onRemove={() => removeColumn(i)}
          />
        ))
      )}

      <button
        type="button"
        onClick={addColumn}
        className="flex items-center gap-1.5 rounded-lg border border-dashed border-brand-300 px-3 py-2 text-sm text-brand-500 transition hover:border-brand-400 hover:bg-brand-50 dark:border-brand-700 dark:hover:bg-brand-500/10"
      >
        <Plus size={15} /> Agregar columna
      </button>
    </div>
  );
};
