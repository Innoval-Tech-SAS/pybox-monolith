import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { Breadcrumb } from "@/ui/components/common/breadcrumb";
import { Loader } from "@/ui/components/loader/loader";
import { useTickets } from "@/support/hooks/use-tickets";
import { useUpdateTicketStatus } from "@/support/hooks/use-update-ticket-status";
import { TicketKanbanBoard } from "@/support/components/ticket-kanban/ticket-kanban-board";
import { TicketKanbanHeader } from "@/support/components/ticket-kanban/ticket-kanban-header";
import type { SupportTicketStatus } from "@/types/support/support-types";
import type { TicketKanbanGroupKey } from "@/types/support/ticket-kanban-types";
import {
  getTicketKanbanGroups,
  mapTicketToKanban,
} from "@/support/utils/ticket-kanban-utils";

export const CustomerServiceHome: React.FC = () => {
  const navigate = useNavigate();
  const { tickets, loading } = useTickets({ includeResolved: true });
  const { updateStatus } = useUpdateTicketStatus();
  const [selectedGroup, setSelectedGroup] =
    useState<TicketKanbanGroupKey>("all");

  const allTickets = useMemo(
    () => tickets.map(mapTicketToKanban),
    [tickets],
  );
  const groups = useMemo(
    () => getTicketKanbanGroups(allTickets),
    [allTickets],
  );

  const handleStatusChange = useCallback(
    (ticketNumber: number, newStatus: SupportTicketStatus) => {
      return updateStatus(ticketNumber, newStatus);
    },
    [updateStatus],
  );

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <Breadcrumb pageTitle="Tickets" />
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto custom-scrollbar rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
        <TicketKanbanHeader
          groups={groups}
          selectedGroup={selectedGroup}
          onSelectGroup={setSelectedGroup}
        />
        {loading ? (
          <div className="flex min-h-105 items-center justify-center border-t border-gray-200 dark:border-white/5">
            <Loader loaderText="Cargando tickets..." />
          </div>
        ) : (
          <TicketKanbanBoard
            tickets={allTickets}
            selectedGroup={selectedGroup}
            onOpenTicket={(ticketId) => navigate(`/cs/tickets/${ticketId}`)}
            onStatusChange={handleStatusChange}
          />
        )}
      </div>
    </div>
  );
};
