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

export const useApiClient = () => {
  const { sendRequest } = useSendRequest();
  const { error: toastError } = useToast();
  const navigate = useNavigate();

  const apiClient = useCallback(
    async (endpoint: string, options: RequestInit = {}) => {
      if (!endpoint.startsWith("/")) throw new Error("endpoint must start with '/'");

      const url = `${API_URL}${endpoint}`;
      const authHeaders = {
        ...getAuthHeaders(),
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers as Record<string, string>),
      };
      let response = await sendRequest(url, { ...options, headers: authHeaders });

      if (response.status === 401) {
        const body = await response.json().catch(() => ({}));
        const message = extractMessage(body, "Error 401");

        if (message === "El token expiró.") {
          const refreshToken = sessionStorage.getItem("refreshToken");
          if (refreshToken) {
            const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (refreshRes.ok) {
              const data = await refreshRes.json();
              sessionStorage.setItem("accessToken", data.accessToken);
              sessionStorage.setItem("refreshToken", data.refreshToken);
              const retryHeaders = {
                ...(options.headers as Record<string, string>),
                Authorization: `Bearer ${data.accessToken}`,
              };
              response = await sendRequest(url, { ...options, headers: retryHeaders });
            } else {
              sessionStorage.clear();
              navigate("/admin/sign-in", { replace: true });
              return null;
            }
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
