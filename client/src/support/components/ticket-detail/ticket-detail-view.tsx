import { Badge } from "@/ui/components/badge";
import { Card, CardTitle } from "@/ui/components/card";
import type { TicketDetailViewProps } from "@/types/props/ticket-detail-view-props";
import {
  formatTicketDetailDate,
  getStatusBadgeStyles,
  TICKET_CASE_TYPE_LABELS,
  TICKET_STATUS_LABELS,
} from "@/support/utils/ticket-kanban-utils";

export const TicketDetailView: React.FC<TicketDetailViewProps> = ({
  ticket,
}) => (
  <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
    <Card>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="mb-2 text-theme-xs font-semibold uppercase text-brand-500 dark:text-brand-400">
            Ticket #{ticket.id}
          </p>
          <h2 className="text-title-sm font-semibold text-gray-800 dark:text-white/90">
            {TICKET_CASE_TYPE_LABELS[ticket.caseType]}
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
            Caso creado para seguimiento de Customer Service.
          </p>
        </div>
        <span
          className={`inline-flex w-fit rounded-full px-2.5 py-1 text-theme-xs font-medium ${getStatusBadgeStyles(ticket.status)}`}
        >
          {TICKET_STATUS_LABELS[ticket.status]}
        </span>
      </div>

      <div className="mt-6 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-white/[0.03]">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Notas
        </p>
        <p className="whitespace-pre-line text-sm text-gray-700 dark:text-gray-300">
          {ticket.notes ?? "Este ticket todavía no tiene notas registradas."}
        </p>
      </div>
    </Card>

    <Card>
      <CardTitle>Detalle del ticket</CardTitle>
      <div className="mt-5 flex flex-col gap-3">
        <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-xs text-gray-400 dark:text-gray-500">Entidad</p>
          <p className="mt-1 break-all text-sm font-medium text-gray-800 dark:text-white/90">
            {ticket.organizationId}
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/[0.03]">
            <p className="text-xs text-gray-400 dark:text-gray-500">Creado por</p>
            <p className="mt-1 text-sm font-medium text-gray-800 dark:text-white/90">
              {ticket.createdBy}
            </p>
          </div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/[0.03]">
            <p className="text-xs text-gray-400 dark:text-gray-500">Asignado a</p>
            <p className="mt-1 text-sm font-medium text-gray-800 dark:text-white/90">
              {ticket.assignedTo ?? "Sin asignar"}
            </p>
          </div>
        </div>
        <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-xs text-gray-400 dark:text-gray-500">Creado</p>
          <p className="mt-1 text-sm font-medium text-gray-800 dark:text-white/90">
            {formatTicketDetailDate(ticket.createdAt)}
          </p>
        </div>
        <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-xs text-gray-400 dark:text-gray-500">Resuelto</p>
          <p className="mt-1 text-sm font-medium text-gray-800 dark:text-white/90">
            {formatTicketDetailDate(ticket.resolvedAt)}
          </p>
        </div>
        <div>
          <Badge color="info" size="sm">
            {ticket.caseType}
          </Badge>
        </div>
      </div>
    </Card>
  </div>
);
