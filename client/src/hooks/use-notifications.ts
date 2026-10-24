import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";
import type { AppNotification } from "@/types/notifications/notification";
import { playNotificationSound } from "@/utils/notification-sound";
import { openNotificationStream } from "@/utils/notification-stream";

export const useNotifications = () => {
  const { apiClient } = useApiClient();
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const data: AppNotification[] = await apiClient("/notifications");
      setNotifications(data);
    } catch (error) {
      // apiClient ya muestra un toast con el mensaje real del backend; esto solo
      // deja rastro en consola para diagnóstico.
      console.error("[notifications] fetch failed", error);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  useEffect(() => { fetchNotifications(); }, [fetchNotifications]);

  // La campana vive fuera de <MfaGuard> (ver admin-layout.tsx), así que este fetch
  // inicial puede correr antes de que el MFA quede verificado y volver 403 sin
  // reintento. "mfa-verified" (emitido por MfaGuard al completar el OTP) es la señal
  // para reintentar sin depender de un refresh manual de página.
  useEffect(() => {
    window.addEventListener("mfa-verified", fetchNotifications);
    return () => window.removeEventListener("mfa-verified", fetchNotifications);
  }, [fetchNotifications]);

  // SSE: receive real-time notifications via /notifications/stream (cookie httpOnly)
  useEffect(() => {
    if (!sessionStorage.getItem("user")) return;

    const es = openNotificationStream();

    es.addEventListener("notification", (e) => {
      try {
        const notif: AppNotification = JSON.parse(e.data);
        setNotifications((prev) => [notif, ...prev]);
        playNotificationSound();
      } catch {
        // malformed event
      }
    });

    es.onerror = () => {
      // Let the browser auto-reconnect; closing here would kill reconnection
    };

    return () => es.close();
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      await apiClient("/notifications/read-all", { method: "POST" });
      setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
    } catch (error) {
      console.error("[notifications] mark_all_read failed", error);
    }
  }, [apiClient]);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  return { notifications, loading, unreadCount, markAllRead, refetch: fetchNotifications };
};
