import { useCallback, useEffect, useState } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import type { SupportTicketStatus } from "@/types/support/support-types";
import type { TicketKanban } from "@/types/support/ticket-kanban-types";
import type { TicketKanbanBoardProps } from "@/types/props/ticket-kanban-board-props";
import {
  getFilteredKanbanTickets,
  getVisibleKanbanColumns,
} from "@/support/utils/ticket-kanban-utils";
import { TicketKanbanColumn } from "./ticket-kanban-column";

const TERMINAL_STATUSES = new Set<SupportTicketStatus>(["RESUELTO", "CERRADO"]);
const TERMINAL_STATUS_LABELS: Record<string, string> = {
  RESUELTO: "Resuelto",
  CERRADO: "Cerrado",
};

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

  const [pendingTerminalMove, setPendingTerminalMove] = useState<{
    ticketId: string;
    ticketNumber: number;
    newStatus: SupportTicketStatus;
  } | null>(null);

  const applyStatusChange = useCallback(
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

  const changeTicketStatus = useCallback(
    (ticketId: string, ticketNumber: number, newStatus: SupportTicketStatus) => {
      // Un drag accidental a una columna terminal (resuelto/cerrado) no debe cerrar el
      // ticket sin querer -- se pide confirmación antes de aplicar el cambio; la tarjeta
      // se queda en su columna actual hasta que el usuario confirme.
      if (TERMINAL_STATUSES.has(newStatus)) {
        setPendingTerminalMove({ ticketId, ticketNumber, newStatus });
        return;
      }
      applyStatusChange(ticketId, ticketNumber, newStatus);
    },
    [applyStatusChange],
  );

  const confirmTerminalMove = () => {
    if (!pendingTerminalMove) return;
    const { ticketId, ticketNumber, newStatus } = pendingTerminalMove;
    setPendingTerminalMove(null);
    applyStatusChange(ticketId, ticketNumber, newStatus);
  };

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

      <ConfirmModal
        isOpen={!!pendingTerminalMove}
        onClose={() => setPendingTerminalMove(null)}
        onConfirm={confirmTerminalMove}
        title="Cerrar ticket"
        message={`¿Mover el ticket #${pendingTerminalMove?.ticketNumber} a "${
          pendingTerminalMove ? TERMINAL_STATUS_LABELS[pendingTerminalMove.newStatus] : ""
        }"? Esta acción marca el ticket como resuelto.`}
        confirmLabel="Mover"
      />
    </DndProvider>
  );
};
