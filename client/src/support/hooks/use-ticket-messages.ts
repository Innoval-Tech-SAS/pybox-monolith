import { useCallback, useEffect, useRef, useState } from "react";
import { useApiClient, API_URL } from "@/hooks/use-api-client";
import type { TicketMessage } from "@/types/support/support-types";

export const useTicketMessages = (ticketNumber: number | undefined) => {
  const { apiClient } = useApiClient();
  const [messages, setMessages] = useState<TicketMessage[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = useCallback(() => {
    if (!ticketNumber) return;
    setLoading(true);
    apiClient(`/cs/tickets/${ticketNumber}/messages`)
      .then((data: TicketMessage[]) => setMessages(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient, ticketNumber]);

  useEffect(() => { fetch(); }, [fetch]);

  // Listen for SSE notifications about new messages on this ticket
  useEffect(() => {
    if (!ticketNumber) return;
    const token = sessionStorage.getItem("accessToken");
    if (!token) return;

    const es = new EventSource(`${API_URL}/notifications/stream?token=${encodeURIComponent(token)}`);
    es.addEventListener("notification", (e) => {
      try {
        const notif = JSON.parse(e.data) as { category?: string; details?: { ticket_number?: number } };
        if (
          notif.category === "support_message" &&
          notif.details?.ticket_number === ticketNumber
        ) {
          fetch();
        }
      } catch {
        // ignore
      }
    });
    es.onerror = () => {};
    return () => es.close();
  }, [ticketNumber, fetch]);

  return { messages, loading, refetch: fetch, setMessages };
};
