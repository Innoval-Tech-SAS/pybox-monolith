import { useCallback } from "react";
import { getAuthHeaders } from "@/utils/auth-headers";
import { useSendRequest } from "./use-send-request";
import { API_URL } from "@/config/api";

export { API_URL };

export const useApiClient = () => {
  const { sendRequest } = useSendRequest();

  const apiClient = useCallback(
    async (endpoint: string, options: RequestInit = {}) => {
      if (!endpoint.startsWith("/")) throw new Error("endpoint must start with '/'");
      return await sendRequest(`${API_URL}${endpoint}`, {
        ...options,
        headers: { ...getAuthHeaders(), ...(options.headers as Record<string, string>) },
      });
    },
    [sendRequest],
  );

  return { apiClient };
};
