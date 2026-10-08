import { Trash2 } from "lucide-react";
import { HAVING_OPS, HAVING_OPS_WITH_MULTIPLE_VALUES } from "@/constants/aggregation-constants";
import type { HavingOp } from "@/types/aggregation-types";
import type { HavingRowProps } from "@/ui/types/step-aggregation-props";
import { selectClass } from "./shared-select-class";

export const HavingRow: React.FC<HavingRowProps> = ({ having, metricOptions, onChange, onRemove }) => {
  const multiValue = HAVING_OPS_WITH_MULTIPLE_VALUES.includes(having.op);

  return (
    <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
      <select
        value={having.metric}
        onChange={(e) => onChange({ metric: e.target.value })}
        className={selectClass}
      >
        {metricOptions.map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>

      <select
        value={having.op}
        onChange={(e) => {
          const op = e.target.value as HavingOp;
          onChange({ op, value: HAVING_OPS_WITH_MULTIPLE_VALUES.includes(op) ? [] : "" });
        }}
        className={selectClass}
      >
        {HAVING_OPS.map((op) => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>

      <input
        type="text"
        placeholder={multiValue ? "val1, val2" : "valor"}
        value={
          multiValue
            ? Array.isArray(having.value) ? having.value.join(", ") : ""
            : (having.value as string) ?? ""
        }
        onChange={(e) => {
          const raw = e.target.value;
          onChange({
            value: multiValue ? raw.split(",").map((v) => v.trim()).filter(Boolean) : raw,
          });
        }}
        className={selectClass}
      />

      <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
        <Trash2 size={13} />
      </button>
    </div>
  );
};
