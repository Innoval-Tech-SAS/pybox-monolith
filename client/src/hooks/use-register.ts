import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { setSessionUser } from "@/auth/utils/auth-session-utils";
import { AuthTokenResponse } from "@/types/auth/auth-types";
import { RegisterRequest } from "@/types/auth/user";

export const useRegister = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = async (data: RegisterRequest, endpoint = "/auth/register"): Promise<AuthTokenResponse> => {
    setLoading(true);
    setError(null);
    try {
      const result: AuthTokenResponse = await apiClient(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      sessionStorage.setItem("accessToken", result.accessToken);
      setSessionUser({ email: data.email });
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
