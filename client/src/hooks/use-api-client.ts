import { useCallback } from "react";
import { useNavigate } from "react-router";
import { useSendRequest } from "./use-send-request";
import { useToast } from "@/context/toast-context";
import { ApiError } from "@/types/api-error";
import { API_URL } from "@/config/api";

export { API_URL };

// Debe coincidir textualmente con el mensaje que lanza `_require_mfa_verified` en
// core/security/dependencies.py. El backend ya exige el segundo factor en cada
// endpoint de negocio (no solo la UI) -- si el flag de sesión del servidor expiró
// pero `sessionStorage.mfaVerified` seguía en "true", sin este chequeo el usuario
// vería este error repetido en cada request sin que la app lo regrese al OTP.
const MFA_PENDING_MESSAGE = "Verificación de dos pasos pendiente.";

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
// El access/refresh token viven en cookies httpOnly: el navegador los adjunta solo,
// el frontend no los lee ni los guarda.
let _refreshPromise: Promise<boolean> | null = null;

const refreshAccessToken = async (): Promise<boolean> => {
  if (_refreshPromise) return _refreshPromise;
  _refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      return res.ok;
    } catch {
      return false;
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
    async <T = any>(
      endpoint: string,
      options: RequestInit = {},
      config: { silentStatuses?: number[] } = {},
    ): Promise<T> => {
      if (!endpoint.startsWith("/")) throw new Error("endpoint must start with '/'");

      const url = `${API_URL}${endpoint}`;
      const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
      const headers = {
        ...(options.body && !isFormData ? { "Content-Type": "application/json" } : {}),
        ...(options.headers as Record<string, string>),
      };
      let response = await sendRequest(url, { ...options, headers });

      if (response.status === 401) {
        const body = await response.json().catch(() => ({}));
        const message = extractMessage(body, "Error 401");

        if (message === "El token expiró.") {
          const refreshed = await refreshAccessToken();
          if (refreshed) {
            response = await sendRequest(url, { ...options, headers });
          } else {
            sessionStorage.clear();
            navigate("/admin/sign-in", { replace: true });
            return null as T;
          }
        } else if (
          message === "Usuario no encontrado" ||
          message === "Sesión expirada. Inicia sesión nuevamente." ||
          message === "Not authenticated"
        ) {
          sessionStorage.clear();
          navigate("/admin/sign-in", { replace: true });
          return null as T;
        } else {
          toastError("Error", message);
          throw new ApiError(message, 401);
        }
      }

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        const message = extractMessage(body, `Error ${response.status}`);

        if (response.status === 403 && message === MFA_PENDING_MESSAGE) {
          sessionStorage.removeItem("mfaVerified");
          window.dispatchEvent(new Event("mfa-pending"));
        }

        if (!config.silentStatuses?.includes(response.status)) {
          toastError("Error", message);
        }
        throw new ApiError(message, response.status);
      }

      if (response.status === 204 || response.headers.get("content-length") === "0") {
        return null as T;
      }
      return await response.json();
    },
    [sendRequest, toastError, navigate],
  );

  return { apiClient };
};
