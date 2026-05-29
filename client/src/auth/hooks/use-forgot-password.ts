import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

export type Channel = "EMAIL" | "SMS";

export interface LookupResult {
  maskedEmail: string | null;
  maskedPhone: string | null;
}

export const useForgotPassword = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const lookup = async (documentType: string, documentNumber: string): Promise<LookupResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient("/auth/forgot-password/lookup", {
        method: "POST",
        body: JSON.stringify({ document_type: documentType, document_number: documentNumber }),
      });
      return { maskedEmail: data.maskedEmail, maskedPhone: data.maskedPhone };
    } catch (e) {
      setError(e instanceof Error ? e.message : "No encontramos una cuenta con ese documento");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const sendCode = async (documentType: string, documentNumber: string, channel: Channel): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await apiClient("/auth/forgot-password/send-code", {
        method: "POST",
        body: JSON.stringify({ document_type: documentType, document_number: documentNumber, channel }),
      });
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al enviar el código");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (
    documentType: string,
    documentNumber: string,
    code: string,
    channel: Channel,
    newPassword: string,
  ): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await apiClient("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ document_type: documentType, document_number: documentNumber, code, channel, new_password: newPassword }),
      });
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al restablecer la contraseña");
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { lookup, sendCode, resetPassword, loading, error, clearError };
};
