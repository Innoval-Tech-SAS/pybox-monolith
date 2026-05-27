export type SupportCaseType = "org_verification" | "error_report";
export type SupportTicketStatus = "open" | "in_progress" | "resolved";

export interface SupportTicket {
  id: string;
  ticketNumber: number;
  caseType: SupportCaseType;
  status: SupportTicketStatus;
  organizationId: string;
  createdBy: number;
  assignedTo: number | null;
  notes: string | null;
  resolvedAt: string | null;
  createdAt: string;
}

export interface UseTicketsOptions {
  includeResolved?: boolean;
}

export interface AssignTicketPayload {
  userId: number;
}

export interface ResolveTicketPayload {
  approved: boolean;
  notes?: string;
}

export interface OrgDoc {
  label: string;
  url: string | null;
}

export interface OrgDocsData {
  orgName: string;
  documents: OrgDoc[];
}
