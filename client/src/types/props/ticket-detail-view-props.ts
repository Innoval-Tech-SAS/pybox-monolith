import type { SupportTicket } from "@/types/support/support-types";

export interface TicketDetailViewProps {
  ticket: SupportTicket;
  onTicketResolved?: (ticket: SupportTicket) => void;
}
