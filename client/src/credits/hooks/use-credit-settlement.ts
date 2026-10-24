import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useToast } from "@/context/toast-context";

/**
 * Autogestión del titular sobre un crédito propio: solicitar la baja adjuntando el
 * comprobante de pago. Crea un ticket "Baja de crédito" hacia la organización dueña;
 * al aprobarlo se registra el pago total y el crédito se desactiva.
 */
export const useCreditSettlement = () => {
  const { apiClient } = useApiClient();
  const { success } = useToast();
  const [submitting, setSubmitting] = useState(false);

  const requestSettlement = async (creditId: string, files: FileList | File[]): Promise<boolean> => {
    setSubmitting(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => formData.append("files", file));
      await apiClient(`/credits/${creditId}/settlement`, {
        method: "POST",
        body: formData,
      });
      success("Solicitud enviada", "Tu baja de crédito quedó en revisión.");
      return true;
    } catch {
      return false;
    } finally {
      setSubmitting(false);
    }
  };

  return { requestSettlement, submitting };
};
