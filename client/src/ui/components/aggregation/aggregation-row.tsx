import { Trash2 } from "lucide-react";
import { AGG_FUNCTIONS } from "@/constants/aggregation-constants";
import type { AggFunction } from "@/types/aggregation-types";
import type { AggregationRowProps } from "@/ui/types/step-aggregation-props";
import { selectClass } from "./shared-select-class";

export const AggregationRow: React.FC<AggregationRowProps> = ({ aggregation, tables, useFields, onChange, onRemove }) => {
  const table = tables.find((t) => t.alias === aggregation.table);
  const { fields } = useFields(table?.name ?? "");
  const isCount = aggregation.function === "count";

  return (
    <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
      <select
        value={aggregation.function}
        onChange={(e) => {
          const fn = e.target.value as AggFunction;
          onChange({ function: fn, column: fn === "count" ? "*" : "" });
        }}
        className={selectClass}
      >
        {AGG_FUNCTIONS.map((fn) => (
          <option key={fn.value} value={fn.value}>{fn.label}</option>
        ))}
      </select>

      <select
        value={aggregation.table}
        onChange={(e) => onChange({ table: e.target.value, column: isCount ? "*" : "" })}
        className={selectClass}
      >
        {tables.map((t) => (
          <option key={t.alias} value={t.alias}>{t.alias}</option>
        ))}
      </select>

      <select
        value={aggregation.column}
        onChange={(e) => onChange({ column: e.target.value })}
        disabled={isCount}
        className={`${selectClass} disabled:opacity-60`}
      >
        {isCount && <option value="*">* (todas las filas)</option>}
        {!isCount && <option value="">Columna…</option>}
        {fields.map((f) => (
          <option key={f.name} value={f.name}>{f.name}</option>
        ))}
      </select>

      <input
        type="text"
        placeholder="alias"
        value={aggregation.alias}
        onChange={(e) => onChange({ alias: e.target.value })}
        className={selectClass}
      />

      <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
        <Trash2 size={13} />
      </button>
    </div>
  );
};
