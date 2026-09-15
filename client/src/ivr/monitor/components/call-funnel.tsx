import { FUNNEL_STEPS, type IvrFunnel } from "../types/ivr-report-types";

interface CallFunnelProps {
  funnel: IvrFunnel;
}

/**
 * Embudo de la campaña. Cada escalón se mide contra el primero (marcadas), que
 * es la lectura útil: "de todo lo que marqué, cuánto llegó hasta aquí".
 */
export const CallFunnel: React.FC<CallFunnelProps> = ({ funnel }) => {
  const base = funnel.dialed || 1;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-white/5 dark:bg-white/3">
      <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white/90">
        Embudo
      </h3>
      <div className="flex flex-col gap-3">
        {FUNNEL_STEPS.map(({ key, label }) => {
          const value = funnel[key];
          const pct = Math.round((value * 100) / base);
          return (
            <div key={key}>
              <div className="mb-1 flex items-baseline justify-between gap-3">
                <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
                <span className="shrink-0 text-sm tabular-nums text-gray-500 dark:text-gray-400">
                  {value} · {pct}%
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                <div
                  className="h-full rounded-full bg-success-500"
                  style={{ width: `${Math.min(100, pct)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
