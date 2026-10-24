import { Trash2 } from "lucide-react";
import type { GroupByRowProps } from "@/ui/types/step-aggregation-props";
import { selectClass } from "./shared-select-class";

export const GroupByRow: React.FC<GroupByRowProps> = ({ group, tables, useFields, onChange, onRemove }) => {
  const table = tables.find((t) => t.alias === group.table);
  const { fields } = useFields(table?.name ?? "");

  return (
    <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
      <select
        value={group.table}
        onChange={(e) => onChange({ table: e.target.value, column: "" })}
        className={selectClass}
      >
        {tables.map((t) => (
          <option key={t.alias} value={t.alias}>{t.alias}</option>
        ))}
      </select>

      <select
        value={group.column}
        onChange={(e) => {
          const column = e.target.value;
          onChange({ column, alias: group.alias || column });
        }}
        className={selectClass}
      >
        <option value="">Columna…</option>
        {fields.map((f) => (
          <option key={f.name} value={f.name}>{f.name}</option>
        ))}
      </select>

      <input
        type="text"
        placeholder="alias (opcional)"
        value={group.alias}
        onChange={(e) => onChange({ alias: e.target.value })}
        className={selectClass}
      />

      <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
        <Trash2 size={13} />
      </button>
    </div>
  );
};
