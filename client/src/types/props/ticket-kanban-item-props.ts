import type { SupportTicketStatus } from "@/types/support/support-types";
import type { TicketKanban } from "@/types/support/ticket-kanban-types";

export interface TicketKanbanItemProps {
  ticket: TicketKanban;
  index: number;
  moveTicket: (dragIndex: number, hoverIndex: number) => void;
  changeTicketStatus: (ticketId: string, ticketNumber: number, newStatus: SupportTicketStatus) => void;
  isTerminal?: boolean;
  onOpenTicket: (ticketId: string) => void;
}
