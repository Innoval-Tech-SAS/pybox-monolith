import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { TicketEvent } from "@/types/support/support-types";

export const useTicketEvents = (ticketNumber: number | undefined) => {
  const { apiClient } = useApiClient();
  const [events, setEvents] = useState<TicketEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = useCallback(() => {
    if (!ticketNumber) return;
    setLoading(true);
    apiClient(`/cs/tickets/${ticketNumber}/events`)
      .then((data: TicketEvent[]) => setEvents(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient, ticketNumber]);

  useEffect(() => { fetch(); }, [fetch]);

  return { events, loading, refetch: fetch };
};
