import { useCallback, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { TicketMessage } from "@/types/support/support-types";

interface SendMessagePayload {
  body: string;
  isInternal?: boolean;
}

export const useSendTicketMessage = (ticketNumber: number) => {
  const { apiClient } = useApiClient();
  const [sending, setSending] = useState(false);

  const sendMessage = useCallback(
    async (payload: SendMessagePayload): Promise<TicketMessage | null> => {
      setSending(true);
      try {
        return await apiClient(`/cs/tickets/${ticketNumber}/messages`, {
          method: "POST",
          body: JSON.stringify({ body: payload.body, is_internal: payload.isInternal ?? false }),
        }) as TicketMessage;
      } catch {
        return null;
      } finally {
        setSending(false);
      }
    },
    [apiClient, ticketNumber],
  );

  return { sendMessage, sending };
};
