import { useCallback, useEffect, useState } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import type { SupportTicketStatus } from "@/types/support/support-types";
import type { TicketKanban } from "@/types/support/ticket-kanban-types";
import type { TicketKanbanBoardProps } from "@/types/props/ticket-kanban-board-props";
import {
  getFilteredKanbanTickets,
  getVisibleKanbanColumns,
} from "@/support/utils/ticket-kanban-utils";
import { TicketKanbanColumn } from "./ticket-kanban-column";

const TERMINAL_STATUSES = new Set<SupportTicketStatus>(["resolved", "closed"]);

export const TicketKanbanBoard: React.FC<TicketKanbanBoardProps> = ({
  tickets,
  selectedGroup,
  onOpenTicket,
  onStatusChange,
}) => {
  const [kanbanTickets, setKanbanTickets] = useState<TicketKanban[]>(tickets);

  useEffect(() => { setKanbanTickets(tickets); }, [tickets]);

  const moveTicket = useCallback((dragIndex: number, hoverIndex: number) => {
    setKanbanTickets((prev) => {
      const next = [...prev];
      const dragged = next[dragIndex];
      if (!dragged) return prev;
      next.splice(dragIndex, 1);
      next.splice(hoverIndex, 0, dragged);
      return next;
    });
  }, []);

  const changeTicketStatus = useCallback(
    (ticketId: string, ticketNumber: number, newStatus: SupportTicketStatus) => {
      // Optimistic update — capture snapshot for rollback
      let snapshot: TicketKanban[] = [];
      setKanbanTickets((prev) => {
        snapshot = prev;
        return prev.map((t) => t.id === ticketId ? { ...t, status: newStatus } : t);
      });
      // Persist + rollback on failure
      onStatusChange?.(ticketNumber, newStatus).then((ok) => {
        if (!ok) setKanbanTickets(snapshot);
      });
    },
    [onStatusChange],
  );

  const filteredTickets = getFilteredKanbanTickets(kanbanTickets, selectedGroup);
  const visibleColumns = getVisibleKanbanColumns(selectedGroup);

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="overflow-x-auto border-t border-gray-200 dark:border-white/5">
        <div
          className="flex min-w-max divide-x divide-gray-200 dark:divide-white/5"
          style={{ minWidth: `${visibleColumns.length * 260}px` }}
        >
          {visibleColumns.map((column) => (
            <TicketKanbanColumn
              key={column.status}
              title={column.title}
              tickets={filteredTickets.filter((t) => t.status === column.status)}
              status={column.status}
              isTerminalColumn={TERMINAL_STATUSES.has(column.status)}
              getTicketIndex={(id) => kanbanTickets.findIndex((t) => t.id === id)}
              moveTicket={moveTicket}
              changeTicketStatus={changeTicketStatus}
              onOpenTicket={onOpenTicket}
            />
          ))}
        </div>
      </div>
    </DndProvider>
  );
};
