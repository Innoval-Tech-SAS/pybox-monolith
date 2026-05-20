import { useState } from "react";
import { useApiClient } from "./use-api-client";

export interface OAuthRegisterRequest {
  provider: string;
  token: string;
  phone_number: string;
  document_type: string;
  document_number: string;
}

export const useOAuthRegister = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const oauthRegister = async (data: OAuthRegisterRequest) => {
    setLoading(true);
    setError(null);
    try {
      return await apiClient("/auth/oauth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Error al registrar con Google";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { oauthRegister, loading, error };
};
