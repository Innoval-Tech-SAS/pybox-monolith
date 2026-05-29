import type { SupportTicket } from "@/types/support/support-types";

export interface CreateTicketModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (ticket: SupportTicket) => void;
}
