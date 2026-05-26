export interface TicketKanban {
  id: string;
  title: string;
  dueDate: string;
  comments?: number;
  links?: number;
  assignee: string;
  status: string;
  description?: string;
  priority: {
    name: string;
    color: string;
  };
}

export interface KanbanDropResult {
  name: string;
}
