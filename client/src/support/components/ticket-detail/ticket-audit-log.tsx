import {
  ArrowRightLeft,
  ArrowUpCircle,
  CheckCircle,
  CircleDot,
  Flag,
  Plus,
  RefreshCw,
  UserCheck,
  XCircle,
} from "lucide-react";
import { useTicketEvents } from "@/support/hooks/use-ticket-events";
import type { TicketEventType } from "@/types/support/support-types";

interface TicketAuditLogProps {
  ticketNumber: number;
}

const EVENT_LABELS: Record<TicketEventType, string> = {
  created: "Ticket creado",
  status_changed: "Estado cambiado",
  priority_changed: "Prioridad cambiada",
  assigned: "Asignado",
  reassigned: "Reasignado",
  escalated: "Escalado",
  resolved: "Resuelto",
  closed: "Cerrado",
  reopened: "Reabierto",
};

const EVENT_ICON: Record<TicketEventType, React.ReactNode> = {
  created: <Plus size={12} />,
  status_changed: <ArrowRightLeft size={12} />,
  priority_changed: <Flag size={12} />,
  assigned: <UserCheck size={12} />,
  reassigned: <UserCheck size={12} />,
  escalated: <ArrowUpCircle size={12} />,
  resolved: <CheckCircle size={12} />,
  closed: <XCircle size={12} />,
  reopened: <RefreshCw size={12} />,
};

const EVENT_COLOR: Record<TicketEventType, string> = {
  created: "bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400",
  status_changed: "bg-gray-100 text-gray-600 dark:bg-white/10 dark:text-gray-400",
  priority_changed: "bg-orange-100 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400",
  assigned: "bg-success-50 text-success-600 dark:bg-success-500/20 dark:text-success-400",
  reassigned: "bg-warning-50 text-warning-600 dark:bg-warning-500/20 dark:text-warning-400",
  escalated: "bg-error-50 text-error-600 dark:bg-error-500/20 dark:text-error-400",
  resolved: "bg-success-50 text-success-600 dark:bg-success-500/20 dark:text-success-400",
  closed: "bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-gray-500",
  reopened: "bg-brand-50 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400",
};

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

export const TicketAuditLog: React.FC<TicketAuditLogProps> = ({ ticketNumber }) => {
  const { events, loading } = useTicketEvents(ticketNumber);

  return (
    <div className="mt-6">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        Historial de cambios
      </p>

      {loading && (
        <p className="text-xs text-gray-400">Cargando historial...</p>
      )}

      {!loading && events.length === 0 && (
        <p className="text-xs text-gray-400">Sin cambios registrados.</p>
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
                  {formatDate(ev.createdAt)} · Usuario #{ev.userId}
                </p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
};
