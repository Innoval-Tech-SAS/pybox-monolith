import type { SupportTicket } from "@/types/support/support-types";

export interface TicketListItemProps {
  ticket: SupportTicket;
  onClick: () => void;
}
