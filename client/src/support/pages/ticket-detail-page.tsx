import { useParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { useTicket } from "@/support/hooks/use-ticket";
import { TicketDetailView } from "@/support/components/ticket-detail/ticket-detail-view";
import { getTicketDisplayId } from "@/support/utils/ticket-kanban-utils";

export const TicketDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { ticket, setTicket, loading, notFound } = useTicket(id);
  const breadcrumbItems = [{ label: "Customer Service", path: "/home" }];

  if (loading) {
    return (
      <ModuleBase pageTitle="Ticket" breadcrumbItems={breadcrumbItems}>
        <div className="flex min-h-105 items-center justify-center">
          <Loader loaderText="Cargando ticket..." />
        </div>
      </ModuleBase>
    );
  }

  if (notFound || !ticket) {
    return (
      <ModuleBase pageTitle="Ticket no encontrado" breadcrumbItems={breadcrumbItems}>
        <div className="flex min-h-105 items-center justify-center text-sm text-gray-500 dark:text-gray-400">
          Ticket no encontrado.
        </div>
      </ModuleBase>
    );
  }

  return (
    <ModuleBase
      pageTitle={getTicketDisplayId(ticket.ticketNumber, ticket.caseType)}
      breadcrumbItems={breadcrumbItems}
    >
      <TicketDetailView ticket={ticket} onTicketResolved={(updated) => setTicket(updated)} />
    </ModuleBase>
  );
};
