import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useToast } from "@/context/toast-context";

/**
 * Autogestión del titular sobre una cuota desde el calendario financiero:
 * solicitar reprogramación (crea ticket "Reprogramación de pago") o reportar un
 * pago con comprobante (crea ticket "Validación de pago").
 */
export const usePaymentSelfService = () => {
  const { apiClient } = useApiClient();
  const { success } = useToast();
  const [submitting, setSubmitting] = useState(false);

  const requestReschedule = async (paymentId: string, newDate: string): Promise<boolean> => {
    setSubmitting(true);
    try {
      await apiClient(`/credits/payments/${paymentId}/reschedule`, {
        method: "POST",
        body: JSON.stringify({ newDate }),
      });
      success("Solicitud enviada", "Tu reprogramación quedó en revisión.");
      return true;
    } catch {
      return false;
    } finally {
      setSubmitting(false);
    }
  };

  const requestValidation = async (paymentId: string, files: FileList | File[]): Promise<boolean> => {
    setSubmitting(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => formData.append("files", file));
      await apiClient(`/credits/payments/${paymentId}/payment-validation`, {
        method: "POST",
        body: formData,
      });
      success("Comprobante enviado", "Tu pago quedó en validación.");
      return true;
    } catch {
      return false;
    } finally {
      setSubmitting(false);
    }
  };

  return { requestReschedule, requestValidation, submitting };
};
