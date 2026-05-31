import { Calendar } from "lucide-react";
import type { SupportTicket } from "@/types/support/support-types";
import {
  getCategoryStyles,
  getPriorityBadgeStyles,
  getStatusBadgeStyles,
  getTicketDisplayId,
  TICKET_CASE_TYPE_LABELS,
  TICKET_PRIORITY_LABELS,
  TICKET_STATUS_LABELS,
} from "@/support/utils/ticket-kanban-utils";

interface TicketListItemProps {
  ticket: SupportTicket;
  onClick: () => void;
}

const STATUS_DOT: Record<string, string> = {
  open: "bg-gray-400 dark:bg-gray-500",
  in_progress: "bg-warning-500",
  resolved: "bg-success-500",
};

const CASE_TYPE_COLOR: Record<string, string> = {
  requirement: "brand",
  incident: "error",
};

export const TicketListItem: React.FC<TicketListItemProps> = ({
  ticket,
  onClick,
}) => {
  const displayId = getTicketDisplayId(ticket.ticketNumber, ticket.caseType);
  const title =
    ticket.title ??
    `${TICKET_CASE_TYPE_LABELS[ticket.caseType]} #${ticket.ticketNumber}`;
  const dateStr = new Date(ticket.createdAt).toLocaleDateString("es-CO", {
    day: "2-digit",
    month: "short",
  });

  return (
    <div
      onClick={onClick}
      className="group flex cursor-pointer items-center gap-3 border-b border-gray-100 px-4 py-3 transition-colors hover:bg-gray-50 dark:border-white/5 dark:hover:bg-white/3"
    >
      <span
        className={`h-2 w-2 shrink-0 rounded-full ${STATUS_DOT[ticket.status] ?? "bg-gray-400"}`}
      />

      <span className="flex-1 truncate text-sm font-medium text-gray-800 dark:text-white/90">
        {title}
      </span>

      <span
        className={`hidden shrink-0 rounded-full px-2 py-0.5 text-xs font-medium sm:inline-flex ${getCategoryStyles(CASE_TYPE_COLOR[ticket.caseType] ?? "default")}`}
      >
        {TICKET_CASE_TYPE_LABELS[ticket.caseType]}
      </span>

      <span
        className={`hidden shrink-0 rounded-full px-2 py-0.5 text-xs font-medium md:inline-flex ${getStatusBadgeStyles(ticket.status)}`}
      >
        {TICKET_STATUS_LABELS[ticket.status]}
      </span>

      <span
        className={`hidden shrink-0 rounded-full px-2 py-0.5 text-xs font-medium lg:inline-flex ${getPriorityBadgeStyles(ticket.priority)}`}
      >
        {TICKET_PRIORITY_LABELS[ticket.priority]}
      </span>

      <span className="hidden shrink-0 items-center gap-1 text-xs text-gray-500 dark:text-gray-400 lg:flex">
        <Calendar size={12} />
        {dateStr}
      </span>

      <span className="shrink-0 font-mono text-xs text-gray-400 dark:text-gray-600">
        {displayId}
      </span>
    </div>
  );
};
