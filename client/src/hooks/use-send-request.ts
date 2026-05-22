import { useCallback } from "react";
import { useNavigate } from "react-router";
import { ApiError } from "@/types/api-error";
import { useToast } from "@/context/toast-context";
import { API_URL } from "@/config/api";

export const useSendRequest = () => {
  const { error: toastError } = useToast();
  const navigate = useNavigate();

  const sendRequest = useCallback(
    async (url: string, options: RequestInit) => {
      let response = await fetch(url, options);

      if (response.status === 401) {
        const body = await response.json().catch(() => ({}));
        const message: string = body?.error ?? `Error 401`;

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
              response = await fetch(url, { ...options, headers: retryHeaders });
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
        } else {
          toastError("Error", message);
          throw new ApiError(message, 401);
        }
      }

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        const message = body?.error ?? `Error ${response.status}`;
        toastError("Error", message);
        throw new ApiError(message, response.status);
      }

      if (response.status === 204 || response.headers.get("content-length") === "0") {
        return null;
      }
      return await response.json();
    },
    [toastError, navigate],
  );

  return { sendRequest };
};
