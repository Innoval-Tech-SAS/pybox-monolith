import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { Breadcrumb } from "@/ui/components/common/breadcrumb";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { useTickets } from "@/support/hooks/use-tickets";
import { TicketKanbanHeader } from "@/support/components/ticket-kanban/ticket-kanban-header";
import { TicketListItem } from "@/support/components/ticket-list/ticket-list-item";
import { getTicketKanbanGroups, mapTicketToKanban } from "@/support/utils/ticket-kanban-utils";
import type { SupportTicket } from "@/types/support/support-types";
import type { TicketKanbanGroupKey } from "@/types/support/ticket-kanban-types";

interface DateGroup {
  label: string;
  tickets: SupportTicket[];
}

function groupByDate(tickets: SupportTicket[]): DateGroup[] {
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);
  const startOfWeek = new Date(startOfToday);
  startOfWeek.setDate(startOfWeek.getDate() - 7);

  const groups: DateGroup[] = [
    { label: "Hoy", tickets: [] },
    { label: "Ayer", tickets: [] },
    { label: "Esta semana", tickets: [] },
    { label: "Anteriores", tickets: [] },
  ];

  for (const ticket of tickets) {
    const d = new Date(ticket.createdAt);
    const startOfDay = new Date(d.getFullYear(), d.getMonth(), d.getDate());

    if (startOfDay.getTime() === startOfToday.getTime()) {
      groups[0].tickets.push(ticket);
    } else if (startOfDay.getTime() === startOfYesterday.getTime()) {
      groups[1].tickets.push(ticket);
    } else if (startOfDay >= startOfWeek) {
      groups[2].tickets.push(ticket);
    } else {
      groups[3].tickets.push(ticket);
    }
  }

  return groups.filter((g) => g.tickets.length > 0);
}

export const TicketsPage: React.FC = () => {
  const navigate = useNavigate();
  const { tickets, loading } = useTickets({ includeResolved: true });
  const [selectedGroup, setSelectedGroup] = useState<TicketKanbanGroupKey>("all");

  const filtered = useMemo(() => {
    if (selectedGroup === "all") return tickets;
    return tickets.filter((t) => t.status === selectedGroup);
  }, [tickets, selectedGroup]);

  const dateGroups = useMemo(() => groupByDate(filtered), [filtered]);

  const groups = useMemo(
    () => getTicketKanbanGroups(tickets.map(mapTicketToKanban)),
    [tickets],
  );

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <Breadcrumb pageTitle="Tickets" />
      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
        <TicketKanbanHeader
          groups={groups}
          selectedGroup={selectedGroup}
          onSelectGroup={setSelectedGroup}
        />

        {loading ? (
          <div className="flex min-h-60 items-center justify-center border-t border-gray-200 dark:border-white/5">
            <Loader loaderText="Cargando tickets..." />
          </div>
        ) : dateGroups.length === 0 ? (
          <div className="flex min-h-60 items-center justify-center border-t border-gray-200 dark:border-white/5">
            <EmptyState title="No hay tickets" />
          </div>
        ) : (
          <div className="border-t border-gray-200 dark:border-white/5">
            {dateGroups.map((group) => (
              <div key={group.label}>
                <div className="flex items-center gap-2 px-4 py-3">
                  <span className="text-sm font-medium text-gray-800 dark:text-white/90">
                    {group.label}
                  </span>
                  <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-white/5 dark:text-gray-400">
                    {group.tickets.length}
                  </span>
                </div>
                {group.tickets.map((ticket) => (
                  <TicketListItem
                    key={ticket.id}
                    ticket={ticket}
                    onClick={() => navigate(`/cs/tickets/${ticket.id}`)}
                  />
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
