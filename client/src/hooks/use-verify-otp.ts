import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { getAuthHeaders } from "@/utils/auth-headers";
import { VerificationChannel } from "@/types/onboarding/onboarding-types";

export const useVerifyOtp = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requestOtp = async (channel: VerificationChannel) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient("/onboarding/request-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ channel }),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Error al enviar el código";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (channel: VerificationChannel, code: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient("/onboarding/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ channel, code }),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Código incorrecto";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { requestOtp, verifyOtp, loading, error, clearError: () => setError(null) };
};
