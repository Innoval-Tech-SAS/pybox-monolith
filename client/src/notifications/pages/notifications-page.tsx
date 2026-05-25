import { useState } from "react";
import { useNavigate } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useNotifications } from "@/hooks/use-notifications";
import { timeAgo } from "@/ui/utils/time-utils";
import type { AppNotification, NotifType } from "@/types/notifications/notification";
import { NotifIcon } from "@/notifications/components/notif-icon";

const TYPE_LABELS: Record<NotifType, string> = {
  success: "Completadas",
  info: "Información",
  warning: "Advertencias",
  error: "Errores",
};

const FILTERS = [
  { key: "all", label: "Todas" },
  { key: "success", label: "Completadas" },
  { key: "info", label: "Información" },
  { key: "warning", label: "Advertencias" },
  { key: "error", label: "Errores" },
] as const;

type FilterKey = (typeof FILTERS)[number]["key"];

const NotificationRow: React.FC<{
  notification: AppNotification;
  onClick: () => void;
}> = ({ notification: n, onClick }) => (
  <button
    onClick={onClick}
    className="w-full flex items-start gap-4 rounded-xl border border-gray-200 bg-white px-5 py-4 text-left transition-colors hover:bg-gray-50 dark:border-gray-800 dark:bg-white/3 dark:hover:bg-white/5"
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

export const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const { notifications, loading, unreadCount, markAllRead } = useNotifications();
  const [filter, setFilter] = useState<FilterKey>("all");

  const filtered = filter === "all"
    ? notifications
    : notifications.filter((n) => n.notifType === filter);

  return (
    <ModuleBase pageTitle="Notificaciones">
      <div className="flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {unreadCount > 0 && (
              <span className="rounded-full bg-brand-500 px-2 py-0.5 text-xs font-medium text-white">
                {unreadCount} nuevas
              </span>
            )}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={markAllRead}
              className="flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
              Marcar todo leído
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
                filter === f.key
                  ? "border-gray-800 bg-gray-900 text-white dark:border-gray-200 dark:bg-white dark:text-gray-900"
                  : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:bg-transparent dark:text-gray-400 dark:hover:bg-white/5"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* List */}
        {loading ? (
          <div className="flex items-center justify-center py-20 text-gray-400">
            Cargando...
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 gap-2">
            <p className="text-sm text-gray-400 dark:text-gray-500">
              {filter === "all" ? "No hay notificaciones" : `No hay notificaciones de tipo "${TYPE_LABELS[filter as NotifType] ?? filter}"`}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {filtered.map((n) => (
              <NotificationRow
                key={n.id}
                notification={n}
                onClick={() => navigate(`/notifications/${n.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </ModuleBase>
  );
};
