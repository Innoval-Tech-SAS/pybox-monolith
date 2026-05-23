import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { setSessionUser } from "@/auth/utils/auth-session-utils";
import { AuthTokenResponse } from "@/types/auth/auth-types";
import { RegisterRequest } from "@/types/auth/user";

export const useRegister = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const register = async (data: RegisterRequest, endpoint = "/auth/register"): Promise<AuthTokenResponse> => {
    setLoading(true);
    try {
      const result: AuthTokenResponse = await apiClient(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      sessionStorage.setItem("accessToken", result.accessToken);
      if (result.refreshToken) sessionStorage.setItem("refreshToken", result.refreshToken);
      setSessionUser({ email: data.email });
      return result;
    } finally {
      setLoading(false);
    }
  };

  return { register, loading };
};
