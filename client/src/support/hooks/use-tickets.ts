import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SupportTicket, TicketFilterParams } from "@/types/support/support-types";

export const useTickets = (params: TicketFilterParams = {}) => {
  const { apiClient } = useApiClient();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTickets = useCallback(() => {
    const qs = new URLSearchParams();
    if (params.includeResolved) qs.set("includeResolved", "true");
    if (params.q) qs.set("q", params.q);
    if (params.status) qs.set("status", params.status);
    if (params.priority) qs.set("priority", params.priority);
    if (params.caseType) qs.set("caseType", params.caseType);
    if (params.assignedTo) qs.set("assignedTo", String(params.assignedTo));
    if (params.fromDate) qs.set("fromDate", params.fromDate);
    if (params.toDate) qs.set("toDate", params.toDate);

    const endpoint = `/cs/tickets?${qs.toString()}`;
    setLoading(true);
    apiClient(endpoint)
      .then((data: SupportTicket[]) => setTickets(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient, params.includeResolved, params.q, params.status, params.priority,
      params.caseType, params.assignedTo, params.fromDate, params.toDate]);

  useEffect(() => { fetchTickets(); }, [fetchTickets]);

  return { tickets, loading, refetch: fetchTickets };
};
