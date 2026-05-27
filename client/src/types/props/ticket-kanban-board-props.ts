import type {
  TicketKanban,
  TicketKanbanGroupKey,
} from "@/types/support/ticket-kanban-types";

export interface TicketKanbanBoardProps {
  tickets: TicketKanban[];
  selectedGroup: TicketKanbanGroupKey;
  onOpenTicket: (ticketId: number) => void;
}
