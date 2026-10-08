export type SupportCaseType = "REQUERIMIENTO" | "INCIDENTE";

export type SupportTicketStatus =
  | "NUEVO"
  | "ABIERTO"
  | "EN_PROGRESO"
  | "PENDIENTE_CLIENTE"
  | "PENDIENTE_TERCERO"
  | "RESUELTO"
  | "CERRADO";

export type SupportTicketPriority = "BAJA" | "MEDIA" | "ALTA" | "URGENTE";

export interface SupportTicket {
  id: string;
  ticketNumber: number;
  caseType: SupportCaseType;
  topic: string | null;
  status: SupportTicketStatus;
  priority: SupportTicketPriority;
  organizationId: string | null;
  organizationName: string;
  createdBy: string;
  assignedTo: string | null;
  title: string | null;
  notes: string | null;
  resolvedAt: string | null;
  closedAt: string | null;
  createdAt: string;
}

export interface TicketCategory {
  label: string;
  topic: string;
  caseType: SupportCaseType;
  description: string;
  icon: string;
}

export interface CreateTicketPayload {
  organizationId?: string;
  title: string;
  topic: string;
  notes: string;
  priority?: SupportTicketPriority;
}

export interface UpdateTicketPriorityPayload {
  priority: SupportTicketPriority;
}

export interface TicketAttachment {
  name: string;
  url: string;
  size: number;
}

export interface TicketOrg {
  id: string;
  name: string;
}

export interface UseTicketsOptions {
  includeResolved?: boolean;
}

export interface AssignTicketPayload {
  userId: string;
}

export interface ResolveTicketPayload {
  approved: boolean;
  notes: string;
}

export interface OrgDoc {
  label: string;
  url: string | null;
}

export interface OrgDocsData {
  orgName: string;
  documents: OrgDoc[];
}

export interface TicketMessage {
  id: string;
  ticketId: string;
  senderId: string;
  body: string;
  isInternal: boolean;
  createdAt: string;
}

export type TicketEventType =
  | "CREADO"
  | "CAMBIO_ESTADO"
  | "CAMBIO_PRIORIDAD"
  | "ASIGNADO"
  | "REASIGNADO"
  | "ESCALADO"
  | "RESUELTO"
  | "CERRADO"
  | "REABIERTO";

export interface TicketEvent {
  id: string;
  ticketId: string;
  userId: string;
  userName: string;
  eventType: TicketEventType;
  fromValue: string | null;
  toValue: string | null;
  createdAt: string;
}

export interface TicketMetrics {
  total: number;
  open: number;
  inProgress: number;
  pending: number;
  resolved: number;
  closed: number;
  createdToday: number;
  resolvedToday: number;
  avgResolutionHours: number | null;
  byPriority: Record<SupportTicketPriority, number>;
}

export interface TicketFilterParams {
  q?: string;
  status?: SupportTicketStatus;
  priority?: SupportTicketPriority;
  caseType?: SupportCaseType;
  assignedTo?: number;
  fromDate?: string;
  toDate?: string;
  includeResolved?: boolean;
}
