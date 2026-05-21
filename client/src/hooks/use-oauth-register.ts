import { useState } from "react";
import { useApiClient } from "./use-api-client";

export interface OAuthRegisterRequest {
  provider: string;
  token: string;
  phone_number?: string;
  nationality?: string;
}

interface AuthTokenResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  authProvider: string;
}

export const useOAuthRegister = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const oauthRegister = async (
    data: OAuthRegisterRequest,
    endpoint = "/auth/oauth",
  ): Promise<AuthTokenResponse> => {
    setLoading(true);
    setError(null);
    try {
      const result: AuthTokenResponse = await apiClient(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      sessionStorage.setItem("accessToken", result.accessToken);
      sessionStorage.setItem("refreshToken", result.refreshToken);
      return result;
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
