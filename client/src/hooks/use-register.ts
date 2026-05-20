import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { RegisterRequest } from "@/types/auth/user";

interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  auth_provider: string;
}

export const useRegister = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = async (data: RegisterRequest): Promise<AuthTokenResponse> => {
    setLoading(true);
    setError(null);
    try {
      const result: AuthTokenResponse = await apiClient("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      sessionStorage.setItem("accessToken", result.access_token);
      return result;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Error al registrar usuario";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { register, loading, error };
};
