import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { Breadcrumb } from "@/ui/components/common/breadcrumb";
import { Loader } from "@/ui/components/loader/loader";
import { useTickets } from "@/support/hooks/use-tickets";
import { TicketKanbanBoard } from "@/support/components/ticket-kanban/ticket-kanban-board";
import { TicketKanbanHeader } from "@/support/components/ticket-kanban/ticket-kanban-header";
import type { TicketKanbanGroupKey } from "@/types/support/ticket-kanban-types";
import {
  getTicketKanbanGroups,
  isTicketFromToday,
  mapTicketToKanban,
} from "@/support/utils/ticket-kanban-utils";

export const CustomerServiceHome: React.FC = () => {
  const navigate = useNavigate();
  const { tickets, loading, refetch } = useTickets({ includeResolved: true });
  const [selectedGroup, setSelectedGroup] =
    useState<TicketKanbanGroupKey>("all");

  const todayTickets = useMemo(
    () => tickets.filter(isTicketFromToday).map(mapTicketToKanban),
    [tickets],
  );
  const groups = useMemo(
    () => getTicketKanbanGroups(todayTickets),
    [todayTickets],
  );

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <Breadcrumb pageTitle="Customer Service" />
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        <TicketKanbanHeader
          groups={groups}
          selectedGroup={selectedGroup}
          loading={loading}
          onSelectGroup={setSelectedGroup}
          onRefresh={refetch}
        />
        {loading ? (
          <div className="flex min-h-[420px] items-center justify-center border-t border-gray-200 dark:border-white/[0.05]">
            <Loader loaderText="Cargando tickets del día..." />
          </div>
        ) : (
          <TicketKanbanBoard
            tickets={todayTickets}
            selectedGroup={selectedGroup}
            onOpenTicket={(ticketId) => navigate(`/cs/tickets/${ticketId}`)}
          />
        )}
      </div>
    </div>
  );
};
