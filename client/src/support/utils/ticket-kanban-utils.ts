import type {
  SupportCaseType,
  SupportTicket,
  SupportTicketPriority,
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
  { title: "Nuevos", status: "new" },
  { title: "Abiertos", status: "open" },
  { title: "En proceso", status: "in_progress" },
  { title: "Pend. cliente", status: "pending_client" },
  { title: "Pend. tercero", status: "pending_third" },
  { title: "Resueltos", status: "resolved" },
  { title: "Cerrados", status: "closed" },
];

export const TICKET_STATUS_LABELS: Record<SupportTicketStatus, string> = {
  new: "Nuevo",
  open: "Abierto",
  in_progress: "En proceso",
  pending_client: "Pend. cliente",
  pending_third: "Pend. tercero",
  resolved: "Resuelto",
  closed: "Cerrado",
};

export const TICKET_PRIORITY_LABELS: Record<SupportTicketPriority, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
  urgent: "Urgente",
};

export const TICKET_CASE_TYPE_LABELS: Record<SupportCaseType, string> = {
  requirement: "Requerimiento",
  incident: "Incidente",
};

export const TICKET_TYPE_LABELS = TICKET_CASE_TYPE_LABELS;

const TICKET_PREFIX: Record<SupportCaseType, string> = {
  requirement: "RT",
  incident: "IT",
};

export const getTicketDisplayId = (ticketNumber: number, caseType: SupportCaseType): string =>
  `${TICKET_PREFIX[caseType]}-${String(ticketNumber).padStart(6, "0")}`;

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
  { name: "Todos", key: "all", count: tickets.length },
  { name: "Nuevos", key: "new", count: tickets.filter((t) => t.status === "new").length },
  { name: "Abiertos", key: "open", count: tickets.filter((t) => t.status === "open").length },
  { name: "En proceso", key: "in_progress", count: tickets.filter((t) => t.status === "in_progress").length },
  { name: "Pend. cliente", key: "pending_client", count: tickets.filter((t) => t.status === "pending_client").length },
  { name: "Pend. tercero", key: "pending_third", count: tickets.filter((t) => t.status === "pending_third").length },
  { name: "Resueltos", key: "resolved", count: tickets.filter((t) => t.status === "resolved").length },
  { name: "Cerrados", key: "closed", count: tickets.filter((t) => t.status === "closed").length },
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
    id: ticket.id,
    ticketId: ticket.ticketNumber,
    title: ticket.title ?? `${TICKET_CASE_TYPE_LABELS[ticket.caseType]} #${ticket.ticketNumber}`,
    dueDate: formatTicketShortDate(ticket.createdAt),
    comments: ticket.notes ? 1 : 0,
    links: 1,
    assigneeInitials: getTicketAssigneeInitials(assignedUserId),
    status: ticket.status,
    priority: ticket.priority,
    description: getTicketDescription(ticket),
    category,
    organizationId: ticket.organizationId,
    createdBy: ticket.createdBy,
    assignedTo: ticket.assignedTo,
    notes: ticket.notes,
    resolvedAt: ticket.resolvedAt,
    closedAt: ticket.closedAt,
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
    case "new":
      return "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-400";
    case "open":
      return "bg-gray-100 text-gray-700 dark:bg-white/3 dark:text-white/80";
    case "in_progress":
      return "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-orange-400";
    case "pending_client":
    case "pending_third":
      return "bg-orange-50 text-orange-700 dark:bg-orange-500/15 dark:text-orange-400";
    case "resolved":
      return "bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-500";
    case "closed":
      return "bg-gray-200 text-gray-600 dark:bg-white/5 dark:text-gray-500";
    default:
      return "bg-gray-100 text-gray-700 dark:bg-white/3 dark:text-white/80";
  }
};

export const getStatusBadgeStyles = (status: SupportTicketStatus): string => {
  switch (status) {
    case "new":
      return "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-400";
    case "open":
      return "bg-gray-100 text-gray-700 dark:bg-white/3 dark:text-white/80";
    case "in_progress":
      return "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-orange-400";
    case "pending_client":
    case "pending_third":
      return "bg-orange-50 text-orange-700 dark:bg-orange-500/15 dark:text-orange-400";
    case "resolved":
      return "bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-500";
    case "closed":
      return "bg-gray-200 text-gray-600 dark:bg-white/5 dark:text-gray-500";
    default:
      return "bg-gray-100 text-gray-700 dark:bg-white/3 dark:text-white/80";
  }
};

export const getPriorityBadgeStyles = (priority: SupportTicketPriority): string => {
  switch (priority) {
    case "urgent":
      return "bg-error-50 text-error-700 dark:bg-error-500/15 dark:text-error-400";
    case "high":
      return "bg-orange-50 text-orange-700 dark:bg-orange-500/15 dark:text-orange-400";
    case "medium":
      return "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-warning-400";
    case "low":
    default:
      return "bg-gray-100 text-gray-600 dark:bg-white/5 dark:text-gray-400";
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
    case "requirement":
      return { name: "Requerimiento", color: "brand" };
    case "incident":
      return { name: "Incidente", color: "error" };
    default:
      return { name: "Soporte", color: "default" };
  }
};

const getTicketDescription = (ticket: SupportTicket): string => {
  if (ticket.notes) return ticket.notes;

  if (ticket.caseType === "requirement") {
    return `Solicitud de revisión documental para la entidad ${ticket.organizationId}.`;
  }

  return `Caso creado por el usuario ${ticket.createdBy}.`;
};

const getTicketAssigneeInitials = (userId: number): string =>
  `U${userId}`.slice(0, 3).toUpperCase();
