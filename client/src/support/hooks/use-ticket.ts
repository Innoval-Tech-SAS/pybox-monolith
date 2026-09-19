import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SupportTicket } from "@/types/support/support-types";

export const useTicket = (ticketId: string | undefined) => {
  const { apiClient } = useApiClient();
  const [ticket, setTicket] = useState<SupportTicket | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const fetchTicket = useCallback(() => {
    if (!ticketId) return;
    setLoading(true);
    apiClient(`/cs/tickets/${ticketId}`, { method: "GET" })
      .then((data: SupportTicket) => setTicket(data))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [apiClient, ticketId]);

  useEffect(() => {
    fetchTicket();
  }, [fetchTicket]);

  return { ticket, setTicket, loading, notFound, refetch: fetchTicket };
};
