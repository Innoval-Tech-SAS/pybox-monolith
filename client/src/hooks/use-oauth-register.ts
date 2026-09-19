import { useState } from "react";
import { useApiClient } from "./use-api-client";
import {
  AuthTokenResponse,
  OAuthRegisterRequest,
} from "@/types/auth/auth-types";

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
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al completar el registro.");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { oauthRegister, loading, error };
};
