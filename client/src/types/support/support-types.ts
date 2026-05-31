export type SupportCaseType = "requirement" | "incident";

export type SupportTicketStatus =
  | "new"
  | "open"
  | "in_progress"
  | "pending_client"
  | "pending_third"
  | "resolved"
  | "closed";

export type SupportTicketPriority = "low" | "medium" | "high" | "urgent";

export interface SupportTicket {
  id: string;
  ticketNumber: number;
  caseType: SupportCaseType;
  status: SupportTicketStatus;
  priority: SupportTicketPriority;
  organizationId: string | null;
  organizationName: string;
  createdBy: number;
  assignedTo: number | null;
  title: string | null;
  notes: string | null;
  resolvedAt: string | null;
  closedAt: string | null;
  createdAt: string;
}

export interface TicketCategory {
  label: string;
  caseType: SupportCaseType;
  description: string;
  icon: string;
}

export interface CreateTicketPayload {
  organizationId?: string;
  title: string;
  caseType: SupportCaseType;
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
  userId: number;
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
  senderId: number;
  body: string;
  isInternal: boolean;
  createdAt: string;
}

export type TicketEventType =
  | "created"
  | "status_changed"
  | "priority_changed"
  | "assigned"
  | "reassigned"
  | "escalated"
  | "resolved"
  | "closed"
  | "reopened";

export interface TicketEvent {
  id: string;
  ticketId: string;
  userId: number;
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
