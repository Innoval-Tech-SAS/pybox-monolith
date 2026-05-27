import type {
  SupportCaseType,
  SupportTicket,
  SupportTicketStatus,
} from "@/types/support/support-types";
import type {
  TicketKanban,
  TicketKanbanCategory,
  TicketKanbanColumnDefinition,
  TicketKanbanGroup,
  TicketKanbanGroupKey,
} from "@/types/support/ticket-kanban-types";

export const TICKET_KANBAN_COLUMNS: TicketKanbanColumnDefinition[] = [
  { title: "Abiertos", status: "open" },
  { title: "En proceso", status: "in_progress" },
  { title: "Resueltos", status: "resolved" },
];

export const TICKET_STATUS_LABELS: Record<SupportTicketStatus, string> = {
  open: "Abierto",
  in_progress: "En proceso",
  resolved: "Resuelto",
};

export const TICKET_CASE_TYPE_LABELS: Record<SupportCaseType, string> = {
  org_verification: "Verificación de entidad",
  error_report: "Reporte de error",
};

export const isTicketFromToday = (ticket: SupportTicket): boolean => {
  const date = new Date(ticket.createdAt);
  const today = new Date();

  return (
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate()
  );
};

export const getTicketKanbanGroups = (
  tickets: TicketKanban[],
): TicketKanbanGroup[] => [
  { name: "All Tickets", key: "all", count: tickets.length },
  {
    name: "Abiertos",
    key: "open",
    count: tickets.filter((ticket) => ticket.status === "open").length,
  },
  {
    name: "En proceso",
    key: "in_progress",
    count: tickets.filter((ticket) => ticket.status === "in_progress").length,
  },
  {
    name: "Resueltos",
    key: "resolved",
    count: tickets.filter((ticket) => ticket.status === "resolved").length,
  },
];

export const getFilteredKanbanTickets = (
  tickets: TicketKanban[],
  selectedGroup: TicketKanbanGroupKey,
): TicketKanban[] => {
  if (selectedGroup === "all") return tickets;

  return tickets.filter((ticket) => ticket.status === selectedGroup);
};

export const getVisibleKanbanColumns = (
  selectedGroup: TicketKanbanGroupKey,
): TicketKanbanColumnDefinition[] => {
  if (selectedGroup === "all") return TICKET_KANBAN_COLUMNS;

  return TICKET_KANBAN_COLUMNS.filter(
    (column) => column.status === selectedGroup,
  );
};

export const mapTicketToKanban = (ticket: SupportTicket): TicketKanban => {
  const category = getTicketCategory(ticket.caseType);
  const assignedUserId = ticket.assignedTo ?? ticket.createdBy;

  return {
    id: String(ticket.id),
    ticketId: ticket.id,
    title: `${TICKET_CASE_TYPE_LABELS[ticket.caseType]} #${ticket.id}`,
    dueDate: formatTicketShortDate(ticket.createdAt),
    comments: ticket.notes ? 1 : 0,
    links: 1,
    assigneeInitials: getTicketAssigneeInitials(assignedUserId),
    status: ticket.status,
    description: getTicketDescription(ticket),
    category,
    organizationId: ticket.organizationId,
    createdBy: ticket.createdBy,
    assignedTo: ticket.assignedTo,
    notes: ticket.notes,
    resolvedAt: ticket.resolvedAt,
    createdAt: ticket.createdAt,
  };
};

export const getCategoryStyles = (color: string): string => {
  switch (color) {
    case "error":
      return "bg-error-50 text-error-700 dark:bg-error-500/15 dark:text-error-400";
    case "success":
      return "bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-400";
    case "brand":
      return "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-400";
    case "orange":
      return "bg-orange-50 text-orange-700 dark:bg-orange-500/15 dark:text-orange-400";
    case "purple":
      return "bg-purple-50 text-purple-700 dark:bg-purple-500/15 dark:text-purple-400";
    default:
      return "bg-gray-100 text-gray-700 dark:bg-gray-500/15 dark:text-gray-400";
  }
};

export const getColumnCountStyles = (status: SupportTicketStatus): string => {
  switch (status) {
    case "open":
      return "bg-gray-100 text-gray-700 dark:bg-white/[0.03] dark:text-white/80";
    case "in_progress":
      return "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-orange-400";
    case "resolved":
      return "bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-500";
    default:
      return "bg-gray-100 text-gray-700 dark:bg-white/[0.03] dark:text-white/80";
  }
};

export const getStatusBadgeStyles = (status: SupportTicketStatus): string => {
  switch (status) {
    case "open":
      return "bg-gray-100 text-gray-700 dark:bg-white/[0.03] dark:text-white/80";
    case "in_progress":
      return "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-orange-400";
    case "resolved":
      return "bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-500";
    default:
      return "bg-gray-100 text-gray-700 dark:bg-white/[0.03] dark:text-white/80";
  }
};

export const formatTicketDetailDate = (iso: string | null): string => {
  if (!iso) return "Pendiente";

  return new Date(iso).toLocaleString("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatTicketShortDate = (iso: string): string => {
  const date = new Date(iso);
  const today = new Date();

  if (
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate()
  ) {
    return "Hoy";
  }

  return date.toLocaleDateString("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

const getTicketCategory = (caseType: SupportCaseType): TicketKanbanCategory => {
  switch (caseType) {
    case "org_verification":
      return { name: "Verificación", color: "brand" };
    case "error_report":
      return { name: "Incidencia", color: "error" };
    default:
      return { name: "Soporte", color: "default" };
  }
};

const getTicketDescription = (ticket: SupportTicket): string => {
  if (ticket.notes) return ticket.notes;

  if (ticket.caseType === "org_verification") {
    return `Solicitud de revisión documental para la entidad ${ticket.organizationId}.`;
  }

  return `Caso creado por el usuario ${ticket.createdBy}.`;
};

const getTicketAssigneeInitials = (userId: number): string =>
  `U${userId}`.slice(0, 3).toUpperCase();
