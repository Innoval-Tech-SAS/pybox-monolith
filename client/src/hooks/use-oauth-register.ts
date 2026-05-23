import { useState } from "react";
import { useApiClient } from "./use-api-client";
import {
  AuthTokenResponse,
  OAuthRegisterRequest,
} from "@/types/auth/auth-types";

export const useOAuthRegister = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const oauthRegister = async (
    data: OAuthRegisterRequest,
    endpoint = "/auth/oauth",
  ): Promise<AuthTokenResponse> => {
    setLoading(true);
    try {
      const result: AuthTokenResponse = await apiClient(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      sessionStorage.setItem("accessToken", result.accessToken);
      if (result.refreshToken) sessionStorage.setItem("refreshToken", result.refreshToken);
      return result;
    } finally {
      setLoading(false);
    }
  };

  return { oauthRegister, loading };
};
