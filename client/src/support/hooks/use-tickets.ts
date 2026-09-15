import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { SupportTicket, TicketFilterParams } from "@/types/support/support-types";

export const useTickets = (params: TicketFilterParams = {}) => {
  const { apiClient } = useApiClient();

  const { data: tickets, loading, refetch } = useAsyncResource<SupportTicket[]>(
    () => {
      const qs = new URLSearchParams();
      if (params.includeResolved) qs.set("includeResolved", "true");
      if (params.q) qs.set("q", params.q);
      if (params.status) qs.set("status", params.status);
      if (params.priority) qs.set("priority", params.priority);
      if (params.caseType) qs.set("caseType", params.caseType);
      if (params.assignedTo) qs.set("assignedTo", String(params.assignedTo));
      if (params.fromDate) qs.set("fromDate", params.fromDate);
      if (params.toDate) qs.set("toDate", params.toDate);

      return apiClient(`/cs/tickets?${qs.toString()}`).then((data: SupportTicket[]) => data ?? []);
    },
    [],
    [
      params.includeResolved, params.q, params.status, params.priority,
      params.caseType, params.assignedTo, params.fromDate, params.toDate,
    ],
  );

  return { tickets, loading, refetch };
};
