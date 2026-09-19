import { useState } from "react";
import { Mail } from "lucide-react";
import type { JudicialInboxPanelProps } from "@/types/props/self-home-props";
import type { JudicialNotification } from "@/credits/types/judicial-types";
import { JUDICIAL_PRIORITY_DOT } from "@/constants/credits/judicial-priority";
import { formatPaymentDate } from "@/credits/utils/financial-calendar-utils";
import { JudicialNotificationDetailModal } from "@/credits/components/judicial-notification-detail-modal";
import { Loader } from "@/ui/components/loader/loader";

/** Buzón judicial: notificaciones emitidas por las entidades sobre las obligaciones. */
export const SelfJudicialInbox: React.FC<JudicialInboxPanelProps> = ({
  items,
  unreadCount,
  priorityLabels,
  loading = false,
  onRead,
}) => {
  const [selected, setSelected] = useState<JudicialNotification | null>(null);

  const openDetail = (item: JudicialNotification) => {
    if (!item.isRead) onRead(item.id);
    setSelected(item);
  };

  return (
  <>
  <section className="flex h-full flex-col rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
    <div className="flex items-start justify-between gap-3 px-5 pt-5">
      <div>
        <h2 className="text-base font-semibold text-gray-800 dark:text-white/90">Buzón judicial</h2>
        <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
          {unreadCount > 0
            ? "Tienes notificaciones pendientes por leer."
            : "No tienes notificaciones pendientes."}
        </p>
      </div>
      {unreadCount > 0 && (
        <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-error-500 text-xs font-semibold text-white">
          {unreadCount}
        </span>
      )}
    </div>

    {loading ? (
      <div className="flex flex-1 min-h-32 items-center justify-center">
        <Loader loaderText="Cargando buzón..." />
      </div>
    ) : items.length === 0 ? (
      <div className="flex flex-1 min-h-32 flex-col items-center justify-center gap-2 px-5 py-10 text-center">
        <span className="flex size-11 items-center justify-center rounded-full bg-gray-50 text-gray-400 dark:bg-gray-800 dark:text-gray-500">
          <Mail size={18} />
        </span>
        <p className="text-sm text-gray-400 dark:text-gray-500">Sin notificaciones judiciales.</p>
      </div>
    ) : (
      <ul className="mt-4 flex flex-1 flex-col overflow-y-auto custom-scrollbar">
        {items.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              onClick={() => openDetail(item)}
              className="flex w-full items-start gap-3 border-t border-gray-100 px-5 py-3 text-left transition hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/40"
            >
              <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-gray-50 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                <Mail size={16} />
              </span>

              <div className="min-w-0 flex-1">
                <p
                  className={`truncate text-sm ${item.isRead ? "text-gray-600 dark:text-gray-400" : "font-semibold text-gray-800 dark:text-white/90"}`}
                >
                  {item.title}
                </p>
                <p className="truncate text-xs text-gray-500 dark:text-gray-400">
                  Entidad: {item.entityName}
                </p>
              </div>

              <div className="flex shrink-0 flex-col items-end gap-1">
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  {formatPaymentDate(item.notifiedAt)}
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {priorityLabels[item.priority] ?? item.priority}
                  </span>
                  <span
                    className={`size-2 rounded-full ${JUDICIAL_PRIORITY_DOT[item.priority] ?? "bg-gray-400"}`}
                  />
                </span>
              </div>
            </button>
          </li>
        ))}
      </ul>
    )}
  </section>
  <JudicialNotificationDetailModal
    notification={selected}
    isOpen={!!selected}
    onClose={() => setSelected(null)}
    priorityLabels={priorityLabels}
  />
  </>
  );
};
