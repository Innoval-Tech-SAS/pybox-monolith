import type { SupportTicketStatus } from "@/types/support/support-types";

export interface TicketConversationProps {
  ticketNumber: number;
  status: SupportTicketStatus;
}
