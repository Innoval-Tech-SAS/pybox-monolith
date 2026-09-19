import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { JudicialNotification } from "@/credits/types/judicial-types";

/** Sube adjuntos a una notificación judicial ya creada. Solo la entidad emisora puede
 * llamarlo; el backend devuelve la notificación con el listado de adjuntos actualizado. */
export const useUploadJudicialAttachments = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const uploadAttachments = async (
    notificationId: string,
    files: File[],
  ): Promise<JudicialNotification | null> => {
    if (!files.length) return null;
    setLoading(true);
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));
      return await apiClient(`/judicial-notifications/${notificationId}/attachments`, {
        method: "POST",
        body: formData,
      });
    } catch {
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { uploadAttachments, loading };
};
