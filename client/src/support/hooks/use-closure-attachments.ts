import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { TicketAttachment } from "@/types/support/support-types";

export const useClosureAttachments = (ticketNumber: number, refreshTrigger?: number) => {
  const { apiClient } = useApiClient();
  const { data: attachments, loading } = useAsyncResource<TicketAttachment[]>(
    () =>
      apiClient(`/cs/tickets/${ticketNumber}/closure-attachments`, { method: "GET" }).then(
        (data: TicketAttachment[]) => data ?? [],
      ),
    [],
    [ticketNumber, refreshTrigger],
  );

  return { attachments, loading };
};
