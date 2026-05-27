import type { TicketKanbanHeaderProps } from "@/types/props/ticket-kanban-header-props";

export const TicketKanbanHeader: React.FC<TicketKanbanHeaderProps> = ({
  groups,
  selectedGroup,
  onSelectGroup,
}) => (
  <div className="flex items-center px-4 py-5 xl:px-6 xl:py-6">
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
                : "bg-white dark:bg-white/3"
            }`}
          >
            {group.count}
          </span>
        </button>
      ))}
    </div>
  </div>
);
