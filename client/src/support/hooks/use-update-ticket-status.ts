import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SupportTicketStatus } from "@/types/support/support-types";

export const useUpdateTicketStatus = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const updateStatus = async (ticketNumber: number, status: SupportTicketStatus): Promise<boolean> => {
    setLoading(true);
    try {
      await apiClient(`/cs/tickets/${ticketNumber}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      return true;
    } catch {
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { updateStatus, loading };
};
