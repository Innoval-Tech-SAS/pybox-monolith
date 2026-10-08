import { Plus } from "lucide-react";
import type { AggregationSectionProps } from "@/ui/types/step-aggregation-props";

export const AggregationSection: React.FC<AggregationSectionProps> = ({ title, description, onAdd, addLabel, disabled, children }) => (
  <div className="rounded-xl border border-gray-200 p-4 dark:border-gray-700">
    <div className="mb-2 flex items-center justify-between">
      <div>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{title}</p>
        <p className="mt-0.5 text-xs text-gray-400 dark:text-gray-500">{description}</p>
      </div>
      <button
        type="button"
        onClick={onAdd}
        disabled={disabled}
        className="flex shrink-0 items-center gap-1 text-xs text-brand-500 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40"
      >
        <Plus size={12} /> {addLabel}
      </button>
    </div>
    {children}
  </div>
);
