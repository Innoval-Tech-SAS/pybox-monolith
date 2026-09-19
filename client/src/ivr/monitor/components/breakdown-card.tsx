import type { IvrBreakdownRow } from "../types/ivr-report-types";

interface BreakdownCardProps {
  title: string;
  rows: IvrBreakdownRow[];
  /** Traduce el valor crudo a algo legible (AMD, nodo, intento…). */
  formatValue?: (value: string | null) => string;
  emptyText?: string;
}

export const BreakdownCard: React.FC<BreakdownCardProps> = ({
  title,
  rows,
  formatValue,
  emptyText = "Sin datos todavía.",
}) => {
  const total = rows.reduce((sum, row) => sum + row.count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-white/5 dark:bg-white/3">
      <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white/90">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">{emptyText}</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {rows.map((row) => (
            <li
              key={row.value ?? "__null__"}
              className="flex items-baseline justify-between gap-3 text-sm"
            >
              <span className="truncate text-gray-700 dark:text-gray-300">
                {formatValue ? formatValue(row.value) : (row.value ?? "Sin reportar")}
              </span>
              <span className="shrink-0 tabular-nums text-gray-500 dark:text-gray-400">
                {row.count}
                {total > 0 && (
                  <span className="ml-1 text-xs text-gray-400">
                    ({Math.round((row.count * 100) / total)}%)
                  </span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
