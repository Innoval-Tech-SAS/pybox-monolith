import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { BulkSendResponse } from "@/bulk-send/types/bulk-send-types";

interface BulkSendParams {
  portfolioId: string;
  channelId: string;
  templateId?: string;
  body?: string;
  subject?: string;
  file: File;
}

export const useBulkSend = () => {
  const { apiClient } = useApiClient();
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<BulkSendResponse | null>(null);

  const send = async (params: BulkSendParams): Promise<boolean> => {
    setSending(true);
    setResult(null);

    const query = new URLSearchParams({ portfolioId: params.portfolioId, channelId: params.channelId });
    if (params.templateId) query.set("templateId", params.templateId);

    const formData = new FormData();
    formData.set("file", params.file);
    if (params.body) formData.set("body", params.body);
    if (params.subject) formData.set("subject", params.subject);

    try {
      const data: BulkSendResponse = await apiClient(
        `/messaging/bulk-send/?${query}`,
        { method: "POST", body: formData },
      );
      setResult(data);
      return true;
    } catch {
      return false;
    } finally {
      setSending(false);
    }
  };

  const reset = () => setResult(null);

  return { send, sending, result, reset };
};
