import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

export const useUploadClosureAttachments = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const uploadClosureAttachments = async (ticketNumber: number, files: File[]): Promise<void> => {
    if (!files.length) return;
    setLoading(true);
    try {
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));
      await apiClient(`/cs/tickets/${ticketNumber}/closure-attachments`, {
        method: "POST",
        body: formData,
      });
    } catch {
      // Silencioso a propósito: el ticket ya se cerró, los adjuntos son
      // best-effort y no deben bloquear el flujo si fallan.
    } finally {
      setLoading(false);
    }
  };

  return { uploadClosureAttachments, loading };
};
