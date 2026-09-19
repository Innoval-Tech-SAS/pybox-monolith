import { CircleDot, ClipboardList } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { useTicketEvents } from "@/support/hooks/use-ticket-events";
import type { TicketAuditLogProps } from "@/support/types/ticket-audit-log-props";
import {
  TICKET_EVENT_LABELS as EVENT_LABELS,
  TICKET_EVENT_ICON as EVENT_ICON,
  TICKET_EVENT_COLOR as EVENT_COLOR,
} from "@/support/constants/ticket-event-styles";
import { formatTicketDateTime as formatDate } from "@/support/utils/format-ticket-datetime";

export const TicketAuditLog: React.FC<TicketAuditLogProps> = ({ ticketNumber }) => {
  const { events, loading } = useTicketEvents(ticketNumber);

  return (
    <div className="mt-6">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        Historial de cambios
      </p>

      {loading && (
        <Loader size="sm" loaderText="Cargando historial..." />
      )}

      {!loading && events.length === 0 && (
        <EmptyState icon={ClipboardList} title="Sin cambios registrados" className="py-4" />
      )}

      {!loading && events.length > 0 && (
        <ol className="relative border-l border-gray-200 dark:border-gray-700">
          {events.map((ev) => (
            <li key={ev.id} className="mb-4 ml-4">
              <span
                className={`absolute -left-3 flex size-6 items-center justify-center rounded-full ${EVENT_COLOR[ev.eventType]}`}
              >
                {EVENT_ICON[ev.eventType] ?? <CircleDot size={12} />}
              </span>
              <div className="pl-1">
                <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                  {EVENT_LABELS[ev.eventType]}
                  {ev.fromValue && ev.toValue && (
                    <span className="font-normal text-gray-500 dark:text-gray-400">
                      {" "}· {ev.fromValue} → {ev.toValue}
                    </span>
                  )}
                  {!ev.fromValue && ev.toValue && (
                    <span className="font-normal text-gray-500 dark:text-gray-400">
                      {" "}· {ev.toValue}
                    </span>
                  )}
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  {formatDate(ev.createdAt)} · {ev.userName}
                </p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
};
