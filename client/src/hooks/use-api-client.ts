import { useCallback } from "react";
import { useNavigate } from "react-router";
import { getAuthHeaders } from "@/utils/auth-headers";
import { useSendRequest } from "./use-send-request";
import { useToast } from "@/context/toast-context";
import { ApiError } from "@/types/api-error";
import { API_URL } from "@/config/api";

export { API_URL };

const extractMessage = (body: Record<string, unknown>, fallback: string): string => {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return (detail as Array<{ msg?: string }>).map((e) => e.msg ?? "").filter(Boolean).join(", ") || fallback;
  }
  return (body?.error as string) ?? fallback;
};

// Module-level singleton: only one refresh request at a time per tab.
// Concurrent 401s all await the same promise instead of each sending their own refresh.
let _refreshPromise: Promise<string | null> | null = null;

const refreshAccessToken = async (): Promise<string | null> => {
  if (_refreshPromise) return _refreshPromise;
  _refreshPromise = (async () => {
    const refreshToken = sessionStorage.getItem("refreshToken");
    if (!refreshToken) return null;
    try {
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return null;
      const data = await res.json();
      sessionStorage.setItem("accessToken", data.accessToken);
      sessionStorage.setItem("refreshToken", data.refreshToken);
      return data.accessToken as string;
    } catch {
      return null;
    }
  })().finally(() => {
    _refreshPromise = null;
  });
  return _refreshPromise;
};

export const useApiClient = () => {
  const { sendRequest } = useSendRequest();
  const { error: toastError } = useToast();
  const navigate = useNavigate();

  const apiClient = useCallback(
    async (endpoint: string, options: RequestInit = {}) => {
      if (!endpoint.startsWith("/")) throw new Error("endpoint must start with '/'");

      const url = `${API_URL}${endpoint}`;
      const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
      const authHeaders = {
        ...getAuthHeaders(),
        ...(options.body && !isFormData ? { "Content-Type": "application/json" } : {}),
        ...(options.headers as Record<string, string>),
      };
      let response = await sendRequest(url, { ...options, headers: authHeaders });

      if (response.status === 401) {
        const body = await response.json().catch(() => ({}));
        const message = extractMessage(body, "Error 401");

        if (message === "El token expiró.") {
          const newAccessToken = await refreshAccessToken();
          if (newAccessToken) {
            const retryHeaders = {
              ...(options.headers as Record<string, string>),
              Authorization: `Bearer ${newAccessToken}`,
            };
            response = await sendRequest(url, { ...options, headers: retryHeaders });
          } else {
            sessionStorage.clear();
            navigate("/admin/sign-in", { replace: true });
            return null;
          }
        } else if (
          message === "Usuario no encontrado" ||
          message === "Sesión expirada. Inicia sesión nuevamente." ||
          message === "Not authenticated"
        ) {
          sessionStorage.clear();
          navigate("/admin/sign-in", { replace: true });
          return null;
        } else {
          toastError("Error", message);
          throw new ApiError(message, 401);
        }
      }

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        const message = extractMessage(body, `Error ${response.status}`);
        toastError("Error", message);
        throw new ApiError(message, response.status);
      }

      if (response.status === 204 || response.headers.get("content-length") === "0") {
        return null;
      }
      return await response.json();
    },
    [sendRequest, toastError, navigate],
  );

  return { apiClient };
};
