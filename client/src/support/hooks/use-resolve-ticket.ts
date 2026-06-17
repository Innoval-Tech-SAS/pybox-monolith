import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { ResolveTicketPayload, SupportTicket } from "@/types/support/support-types";

export const useResolveTicket = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const resolveTicket = async (ticketId: string, payload: ResolveTicketPayload): Promise<SupportTicket | null> => {
    setLoading(true);
    try {
      return await apiClient(`/cs/tickets/${ticketId}/resolve`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { resolveTicket, loading };
};
