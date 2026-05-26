import { useState } from "react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useNotifications } from "@/hooks/use-notifications";
import type { NotifType } from "@/types/notifications/notification";
import { FILTERS, FilterKey, TYPE_LABELS } from "@/constants/notifications/notification-filters";
import { NotificationRow } from "@/notifications/components/notification-row";
import { NotificationDetailView } from "@/notifications/components/notification-detail-view";

export const NotificationsPage: React.FC = () => {
  const { notifications, loading, unreadCount, markAllRead } = useNotifications();
  const [filter, setFilter] = useState<FilterKey>("all");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const filtered = filter === "all"
    ? notifications
    : notifications.filter((n) => n.notifType === filter);

  const selected = selectedId !== null
    ? notifications.find((n) => n.id === selectedId) ?? null
    : null;

  return (
    <ModuleBase pageTitle="Notificaciones">
      <div className="flex gap-0">
        {/* Left panel — list */}
        <div
          className={`flex flex-col gap-4 shrink-0 lg:w-96 lg:border-r lg:border-gray-100 lg:pr-6 lg:dark:border-gray-800 ${
            selected ? "hidden lg:flex" : "flex w-full"
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
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

          {loading ? (
            <div className="flex items-center justify-center py-20 text-gray-400">
              Cargando...
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 gap-2">
              <p className="text-sm text-gray-400 dark:text-gray-500">
                {filter === "all"
                  ? "No hay notificaciones"
                  : `No hay notificaciones de tipo "${TYPE_LABELS[filter as NotifType] ?? filter}"`}
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {filtered.map((n) => (
                <NotificationRow
                  key={n.id}
                  notification={n}
                  isSelected={n.id === selectedId}
                  onClick={() => setSelectedId(n.id === selectedId ? null : n.id)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right panel — detail */}
        <div
          className={`min-w-0 flex-1 ${
            selected
              ? "flex flex-col lg:pl-6"
              : "hidden lg:flex items-center justify-center"
          }`}
        >
          {selected ? (
            <>
              <button
                onClick={() => setSelectedId(null)}
                className="mb-4 flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 lg:hidden"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="19" y1="12" x2="5" y2="12" />
                  <polyline points="12 19 5 12 12 5" />
                </svg>
                Volver a notificaciones
              </button>
              <NotificationDetailView notification={selected} />
            </>
          ) : (
            <div className="flex flex-col items-center justify-center gap-3 text-gray-400 dark:text-gray-600">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              <p className="text-sm">Selecciona una notificación</p>
            </div>
          )}
        </div>
      </div>
    </ModuleBase>
  );
};
