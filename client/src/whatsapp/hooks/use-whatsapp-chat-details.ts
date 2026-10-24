import { useCallback, useState } from "react";
import { useApiClient } from "../../hooks/use-api-client";
import type { WhatsAppChatDetails } from "../types/whatsapp-chat-types";

export const useWhatsAppChatDetails = () => {
  const { apiClient } = useApiClient();
  const [details, setDetails] = useState<WhatsAppChatDetails | null>(null);
  const [loading, setLoading] = useState(false);

  const loadDetails = useCallback(
    async (chatId: string, organizationId: string) => {
      setLoading(true);
      setDetails(null);
      try {
        const data = await apiClient<WhatsAppChatDetails>(
          `/whatsapp/chats/${chatId}/details?organizationId=${organizationId}`,
        );
        setDetails(data);
      } finally {
        setLoading(false);
      }
    },
    [apiClient],
  );

  const reset = useCallback(() => setDetails(null), []);

  return { details, loading, loadDetails, reset };
};
