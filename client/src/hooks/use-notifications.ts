import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";
import type { AppNotification } from "@/types/notifications/notification";

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
