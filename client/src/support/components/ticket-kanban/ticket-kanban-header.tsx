import { RefreshCw, SlidersHorizontal } from "lucide-react";
import type { TicketKanbanHeaderProps } from "@/types/props/ticket-kanban-header-props";

export const TicketKanbanHeader: React.FC<TicketKanbanHeaderProps> = ({
  groups,
  selectedGroup,
  loading,
  onSelectGroup,
  onRefresh,
}) => (
  <div className="flex flex-col items-center px-4 py-5 xl:px-6 xl:py-6">
    <div className="flex w-full flex-col gap-5 sm:justify-between xl:flex-row xl:items-center">
      <div className="grid grid-cols-2 items-center gap-x-1 gap-y-2 rounded-lg bg-gray-100 p-0.5 dark:bg-gray-900 sm:grid-cols-4">
        {groups.map((group) => (
          <button
            key={group.key}
            onClick={() => onSelectGroup(group.key)}
            className={`inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium group hover:text-gray-900 dark:hover:text-white xl:justify-start ${
              selectedGroup === group.key
                ? "bg-white text-gray-900 dark:bg-gray-800 dark:text-white"
                : "text-gray-500 dark:text-gray-400"
            }`}
          >
            {group.name}
            <span
              className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium leading-normal group-hover:bg-brand-50 group-hover:text-brand-500 dark:group-hover:bg-brand-500/15 dark:group-hover:text-brand-400 ${
                selectedGroup === group.key
                  ? "bg-brand-50 text-brand-500 dark:bg-brand-500/15 dark:text-brand-400"
                  : "bg-white dark:bg-white/[0.03]"
              }`}
            >
              {group.count}
            </span>
          </button>
        ))}
      </div>
      <div className="flex flex-wrap items-center gap-3 xl:justify-end">
        <button
          type="button"
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/[0.03] dark:hover:text-gray-200"
        >
          <SlidersHorizontal size={20} />
          Filter & Short
        </button>
        <button
          type="button"
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Actualizar
          <RefreshCw className={loading ? "animate-spin" : ""} size={20} />
        </button>
      </div>
    </div>
  </div>
);
