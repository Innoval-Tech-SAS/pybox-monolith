import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { AppNotification } from "@/types/notifications/notification";

/** Detalle de una notificación por id, con estado {data, loading, error} vía useAsyncResource. */
export const useNotificationDetail = (id: string | undefined) => {
  const { apiClient } = useApiClient();

  const fetcher = useCallback((): Promise<AppNotification | null> => {
    if (!id) return Promise.resolve(null);
    return apiClient<AppNotification>(`/notifications/${id}`);
  }, [id, apiClient]);

  const { data: notification, loading, error, refetch } = useAsyncResource<AppNotification | null>(
    fetcher,
    null,
    [fetcher],
  );

  const notFound = !loading && (error !== null || notification === null);

  return { notification, loading, notFound, refetch };
};
