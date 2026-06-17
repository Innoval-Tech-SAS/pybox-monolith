import type { SupportTicketPriority, SupportTicketStatus } from "./support-types";

export type TicketKanbanCategoryColor =
  | "error"
  | "success"
  | "brand"
  | "orange"
  | "purple"
  | "default";

export type TicketKanbanGroupKey = "all" | SupportTicketStatus;

export interface TicketKanbanCategory {
  name: string;
  color: TicketKanbanCategoryColor;
}

export interface TicketKanban {
  id: string;
  ticketId: number;
  title: string;
  dueDate: string;
  comments: number;
  links?: number;
  assigneeInitials: string;
  status: SupportTicketStatus;
  priority: SupportTicketPriority;
  description?: string;
  category: TicketKanbanCategory;
  organizationId: string;
  createdBy: string;
  assignedTo: string | null;
  notes: string | null;
  resolvedAt: string | null;
  closedAt: string | null;
  createdAt: string;
}

export interface TicketKanbanDropResult {
  name: SupportTicketStatus;
}

export interface TicketKanbanDragItem extends TicketKanban {
  index: number;
}

export interface TicketKanbanGroup {
  name: string;
  key: TicketKanbanGroupKey;
  count: number;
}

export interface TicketKanbanColumnDefinition {
  title: string;
  status: SupportTicketStatus;
}
