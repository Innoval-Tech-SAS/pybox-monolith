import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { CreateTicketPayload, SupportTicket } from "@/types/support/support-types";

export const useCreateTicket = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const createTicket = async (payload: CreateTicketPayload): Promise<SupportTicket | null> => {
    setLoading(true);
    try {
      return await apiClient("/cs/tickets", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { createTicket, loading };
};
