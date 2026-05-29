import { useCallback, useEffect, useState } from "react";
import { useApiClient, API_URL } from "./use-api-client";
import type { AppNotification } from "@/types/notifications/notification";
import { playNotificationSound } from "@/utils/notification-sound";

export const useNotifications = () => {
  const { apiClient } = useApiClient();
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const data: AppNotification[] = await apiClient("/notifications");
      setNotifications(data);
    } catch {
      // endpoint not yet implemented
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  useEffect(() => { fetchNotifications(); }, [fetchNotifications]);

  // SSE: receive real-time notifications via /notifications/stream?token=<jwt>
  useEffect(() => {
    const token = sessionStorage.getItem("accessToken");
    if (!token) return;

    const es = new EventSource(`${API_URL}/notifications/stream?token=${encodeURIComponent(token)}`);

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
    } catch {
      // endpoint not yet implemented
    }
  }, [apiClient]);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  return { notifications, loading, unreadCount, markAllRead, refetch: fetchNotifications };
};
