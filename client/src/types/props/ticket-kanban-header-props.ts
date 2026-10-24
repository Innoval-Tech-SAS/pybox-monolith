import type {
  TicketKanbanGroup,
  TicketKanbanGroupKey,
} from "@/types/support/ticket-kanban-types";

export interface TicketKanbanHeaderProps {
  groups: TicketKanbanGroup[];
  selectedGroup: TicketKanbanGroupKey;
  onSelectGroup: (group: TicketKanbanGroupKey) => void;
}
