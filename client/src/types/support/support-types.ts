export type SupportCaseType = "requirement" | "incident";
export type SupportTicketStatus = "open" | "in_progress" | "resolved";

export interface SupportTicket {
  id: string;
  ticketNumber: number;
  caseType: SupportCaseType;
  status: SupportTicketStatus;
  organizationId: string;
  organizationName: string;
  createdBy: number;
  assignedTo: number | null;
  title: string | null;
  notes: string | null;
  resolvedAt: string | null;
  createdAt: string;
}

export interface TicketCategory {
  label: string;
  caseType: SupportCaseType;
  description: string;
  icon: string;
}

export interface CreateTicketPayload {
  organizationId: string;
  title: string;
  caseType: SupportCaseType;
  notes: string;
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
