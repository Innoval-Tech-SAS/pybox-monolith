import type { SupportTicketStatus } from "@/types/support/support-types";
import type { TicketKanban } from "@/types/support/ticket-kanban-types";

export interface TicketKanbanColumnProps {
  title: string;
  tickets: TicketKanban[];
  status: SupportTicketStatus;
  getTicketIndex: (ticketId: string) => number;
  moveTicket: (dragIndex: number, hoverIndex: number) => void;
  changeTicketStatus: (ticketId: string, ticketNumber: number, newStatus: SupportTicketStatus) => void;
  onOpenTicket: (ticketId: string) => void;
  isTerminalColumn?: boolean;
}
