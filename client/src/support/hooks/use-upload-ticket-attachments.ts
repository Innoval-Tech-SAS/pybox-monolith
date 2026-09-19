import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

export const useUploadTicketAttachments = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const uploadAttachments = async (ticketNumber: number, files: File[]): Promise<void> => {
    if (!files.length) return;
    setLoading(true);
    try {
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));
      await apiClient(`/cs/tickets/${ticketNumber}/attachments`, {
        method: "POST",
        body: formData,
      });
    } catch {
      // non-critical — ticket already created
    } finally {
      setLoading(false);
    }
  };

  return { uploadAttachments, loading };
};
