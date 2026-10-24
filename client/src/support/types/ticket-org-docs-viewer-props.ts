import type { SupportTicket } from "@/types/support/support-types";

export interface TicketOrgDocsViewerProps {
  ticket: SupportTicket;
  onResolved: (updated: SupportTicket) => void;
}
