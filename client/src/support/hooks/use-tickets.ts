import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SupportTicket } from "@/types/support/support-types";

export const useTickets = () => {
  const { apiClient } = useApiClient();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTickets = useCallback(() => {
    setLoading(true);
    apiClient("/cs/tickets", { method: "GET" })
      .then((data: SupportTicket[]) => setTickets(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  return { tickets, loading, refetch: fetchTickets };
};
