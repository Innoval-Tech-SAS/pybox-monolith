import type { StatCardProps } from "@/types/props/stat-card-props";

/**
 * Card de contador: label pequeño en mayúsculas arriba, numeral grande y liviano como foco visual.
 * `accent` usa brand-500 para la métrica protagonista; el resto queda en gris para no competir.
 */
export const StatCard: React.FC<StatCardProps> = ({ icon, label, value, accent = false }) => (
  <div
    className={`rounded-2xl border bg-white p-5 dark:bg-white/3 ${
      accent ? "border-brand-200 dark:border-brand-500/30" : "border-gray-200 dark:border-gray-800"
    }`}
  >
    <div className="flex items-center gap-2">
      <span
        className={`flex h-9 w-9 items-center justify-center rounded-lg ${
          accent
            ? "bg-brand-50 text-brand-500 dark:bg-brand-500/15 dark:text-brand-400"
            : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
        }`}
      >
        {icon}
      </span>
      <span className="text-theme-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        {label}
      </span>
    </div>
    <p
      className={`mt-3 text-title-md font-extralight ${
        accent ? "text-brand-500 dark:text-brand-400" : "text-gray-800 dark:text-white/90"
      }`}
    >
      {value}
    </p>
  </div>
);
