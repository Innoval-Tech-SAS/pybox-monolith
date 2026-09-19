import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SupportTicket } from "@/types/support/support-types";

export const useEscalateTicket = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const escalateTicket = async (ticketNumber: number): Promise<SupportTicket | null> => {
    setLoading(true);
    try {
      return await apiClient(`/cs/tickets/${ticketNumber}/escalate`, { method: "POST" });
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { escalateTicket, loading };
};
