import { Trash2 } from "lucide-react";
import type { SortDirection } from "@/types/aggregation-types";
import type { OrderByRowProps } from "@/ui/types/step-aggregation-props";
import { selectClass } from "./shared-select-class";

export const OrderByRow: React.FC<OrderByRowProps> = ({ order, fieldOptions, onChange, onRemove }) => (
  <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
    <select
      value={order.field}
      onChange={(e) => onChange({ field: e.target.value })}
      className={selectClass}
    >
      {fieldOptions.map((f) => (
        <option key={f} value={f}>{f}</option>
      ))}
    </select>

    <select
      value={order.direction}
      onChange={(e) => onChange({ direction: e.target.value as SortDirection })}
      className={selectClass}
    >
      <option value="asc">Ascendente</option>
      <option value="desc">Descendente</option>
    </select>

    <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
      <Trash2 size={13} />
    </button>
  </div>
);
