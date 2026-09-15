import type { IvrOutcomeRow } from "../types/ivr-report-types";

interface OutcomeDistributionProps {
  outcomes: IvrOutcomeRow[];
  typifiedCalls: number;
  totalCalls: number;
}

export const OutcomeDistribution: React.FC<OutcomeDistributionProps> = ({
  outcomes,
  typifiedCalls,
  totalCalls,
}) => {
  const untypified = Math.max(0, totalCalls - typifiedCalls);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-white/5 dark:bg-white/3">
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-base font-semibold text-gray-800 dark:text-white/90">
          Resultados
        </h3>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {typifiedCalls} de {totalCalls} llamadas tipificadas
        </span>
      </div>

      {outcomes.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Todavía no hay resultados. Se registran cuando las llamadas terminan y el flujo
          tiene etiquetas configuradas (botón "Resultados" del diseñador).
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {outcomes.map((row) => (
            <div key={row.key}>
              <div className="mb-1 flex items-baseline justify-between gap-3">
                <span className="truncate text-sm text-gray-700 dark:text-gray-300">
                  {row.label ?? (
                    <span className="text-gray-400 dark:text-gray-500">
                      Sin etiqueta <code className="text-xs">({row.key})</code>
                    </span>
                  )}
                </span>
                <span className="shrink-0 text-sm tabular-nums text-gray-500 dark:text-gray-400">
                  {row.count} · {row.percentage}%
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                <div
                  className="h-full rounded-full bg-brand-500"
                  style={{ width: `${Math.min(100, row.percentage)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {untypified > 0 && (
        <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
          {untypified} llamada{untypified === 1 ? "" : "s"} sin resultado resuelto (aún en curso
          o sin desenlace reportado por Helena).
        </p>
      )}
    </div>
  );
};
