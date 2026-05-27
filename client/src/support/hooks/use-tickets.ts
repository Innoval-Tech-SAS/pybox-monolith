import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  SupportTicket,
  UseTicketsOptions,
} from "@/types/support/support-types";

export const useTickets = ({ includeResolved = false }: UseTicketsOptions = {}) => {
  const { apiClient } = useApiClient();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTickets = useCallback(() => {
    const endpoint = includeResolved
      ? "/cs/tickets?includeResolved=true"
      : "/cs/tickets";

    setLoading(true);
    apiClient(endpoint, { method: "GET" })
      .then((data: SupportTicket[]) => setTickets(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient, includeResolved]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  return { tickets, loading, refetch: fetchTickets };
};
