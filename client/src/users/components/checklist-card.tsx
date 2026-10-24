import type { ChecklistCardProps } from "@/users/types/props/checklist-card-props";

export const ChecklistCard: React.FC<ChecklistCardProps> = ({ icon, title, children }) => (
  <div className="flex flex-col gap-3">
    <div className="flex items-center gap-2">
      {icon}
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h3>
    </div>
    <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
      <ul className="flex flex-col">{children}</ul>
    </div>
  </div>
);
