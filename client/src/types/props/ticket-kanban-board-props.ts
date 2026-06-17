import type { SupportTicketStatus } from "@/types/support/support-types";
import type {
  TicketKanban,
  TicketKanbanGroupKey,
} from "@/types/support/ticket-kanban-types";

export interface TicketKanbanBoardProps {
  tickets: TicketKanban[];
  selectedGroup: TicketKanbanGroupKey;
  onOpenTicket: (ticketId: string) => void;
  onStatusChange?: (ticketNumber: number, newStatus: SupportTicketStatus) => Promise<boolean>;
}
