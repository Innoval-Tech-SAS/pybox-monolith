import type { MetricCardProps } from "@/support/types/metric-card-props";

export const MetricCard: React.FC<MetricCardProps> = ({ label, value, accent }) => (
  <div className="flex flex-col items-center rounded-xl border border-gray-100 bg-white px-4 py-3 dark:border-gray-800 dark:bg-white/3">
    <span className={`text-2xl font-bold ${accent ?? "text-gray-800 dark:text-white/90"}`}>{value}</span>
    <span className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{label}</span>
  </div>
);
