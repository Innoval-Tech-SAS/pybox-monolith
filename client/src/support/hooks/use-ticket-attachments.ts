import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { TicketAttachment } from "@/types/support/support-types";

export const useTicketAttachments = (ticketNumber: number) => {
  const { apiClient } = useApiClient();
  const [attachments, setAttachments] = useState<TicketAttachment[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAttachments = useCallback(() => {
    setLoading(true);
    apiClient(`/cs/tickets/${ticketNumber}/attachments`, { method: "GET" })
      .then((data: TicketAttachment[]) => setAttachments(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient, ticketNumber]);

  useEffect(() => {
    fetchAttachments();
  }, [fetchAttachments]);

  return { attachments, loading, refetch: fetchAttachments };
};
