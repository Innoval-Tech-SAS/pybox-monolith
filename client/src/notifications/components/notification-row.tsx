import { NotifIcon } from "./notif-icon";
import { timeAgo } from "@/ui/utils/time-utils";
import type { NotificationRowProps } from "@/types/props/notification-row-props";

export const NotificationRow: React.FC<NotificationRowProps> = ({ notification: n, isSelected, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className={`w-full flex items-start gap-4 rounded-xl border px-5 py-4 text-left transition-colors ${
      isSelected
        ? "border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-500/10"
        : "border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-800 dark:bg-white/3 dark:hover:bg-white/5"
    }`}
  >
    <NotifIcon type={n.notifType} size="md" />
    <div className="min-w-0 flex-1">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-semibold text-gray-800 dark:text-white/90">
          {n.title}
        </p>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">
            {timeAgo(n.createdAt)}
          </span>
          {!n.isRead && (
            <span className="h-2 w-2 rounded-full bg-brand-500 shrink-0" />
          )}
        </div>
      </div>
      <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400 line-clamp-1">
        {n.body}
      </p>
      <div className="mt-2">
        <span className="inline-flex items-center gap-1 rounded-md border border-gray-200 px-2 py-0.5 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-400">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M3 9h18" /><path d="M9 21V9" /></svg>
          {n.category}
        </span>
      </div>
    </div>
  </button>
);
