import type { StatItemProps } from "@/bulk-send/types/stat-item-props";

export const StatItem: React.FC<StatItemProps> = ({ icon, label, value }) => (
  <div className="flex flex-col items-center gap-1 rounded-xl border border-gray-100 p-4 text-center dark:border-gray-800">
    {icon}
    <span className="text-2xl font-semibold text-gray-800 dark:text-white">{value}</span>
    <span className="text-xs text-gray-500 dark:text-gray-400">{label}</span>
  </div>
);
