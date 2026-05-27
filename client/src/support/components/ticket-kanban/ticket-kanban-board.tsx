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

export const TicketKanbanBoard: React.FC<TicketKanbanBoardProps> = ({
  tickets,
  selectedGroup,
  onOpenTicket,
  onStatusChange,
}) => {
  const [kanbanTickets, setKanbanTickets] = useState<TicketKanban[]>(tickets);

  useEffect(() => {
    setKanbanTickets(tickets);
  }, [tickets]);

  const moveTicket = useCallback((dragIndex: number, hoverIndex: number) => {
    setKanbanTickets((previousTickets) => {
      const newTickets = [...previousTickets];
      const draggedTicket = newTickets[dragIndex];

      if (!draggedTicket) return previousTickets;

      newTickets.splice(dragIndex, 1);
      newTickets.splice(hoverIndex, 0, draggedTicket);
      return newTickets;
    });
  }, []);

  const changeTicketStatus = useCallback(
    (ticketId: string, ticketNumber: number, newStatus: SupportTicketStatus) => {
      setKanbanTickets((previousTickets) =>
        previousTickets.map((ticket) =>
          ticket.id === ticketId ? { ...ticket, status: newStatus } : ticket,
        ),
      );
      onStatusChange?.(ticketNumber, newStatus);
    },
    [onStatusChange],
  );

  const filteredTickets = getFilteredKanbanTickets(kanbanTickets, selectedGroup);
  const visibleColumns = getVisibleKanbanColumns(selectedGroup);
  const gridColumns =
    visibleColumns.length === 1
      ? "sm:grid-cols-1 xl:grid-cols-1"
      : "sm:grid-cols-2 xl:grid-cols-3";

  return (
    <DndProvider backend={HTML5Backend}>
      <div
        className={`mt-7 grid grid-cols-1 divide-x divide-gray-200 border-t border-gray-200 dark:divide-white/5 dark:border-white/5 sm:mt-0 ${gridColumns}`}
      >
        {visibleColumns.map((column) => (
          <TicketKanbanColumn
            key={column.status}
            title={column.title}
            tickets={filteredTickets.filter(
              (ticket) => ticket.status === column.status,
            )}
            status={column.status}
            getTicketIndex={(ticketId) =>
              kanbanTickets.findIndex((ticket) => ticket.id === ticketId)
            }
            moveTicket={moveTicket}
            changeTicketStatus={changeTicketStatus}
            onOpenTicket={onOpenTicket}
          />
        ))}
      </div>
    </DndProvider>
  );
};
