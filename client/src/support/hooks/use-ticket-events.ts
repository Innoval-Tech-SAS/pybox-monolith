import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { TicketEvent } from "@/types/support/support-types";

export const useTicketEvents = (ticketNumber: number | undefined) => {
  const { apiClient } = useApiClient();
  const { data: events, loading, refetch } = useAsyncResource<TicketEvent[]>(
    () =>
      ticketNumber
        ? apiClient(`/cs/tickets/${ticketNumber}/events`).then((data: TicketEvent[]) => data ?? [])
        : Promise.resolve([]),
    [],
    [ticketNumber],
  );

  return { events, loading, refetch };
};
