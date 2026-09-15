import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { JudicialNotification, JudicialNotificationCreatePayload } from "@/credits/types/judicial-types";

/** Notificaciones judiciales emitidas sobre un crédito, del lado de la entidad. */
export const useCreditJudicialNotifications = (creditId: string) => {
  const { apiClient } = useApiClient();
  const [creating, setCreating] = useState(false);

  const fetchItems = () => {
    if (!creditId) return Promise.resolve([]);
    return apiClient(`/judicial-notifications/credits/${creditId}`) as Promise<JudicialNotification[]>;
  };

  const { data: items, loading, error, refetch, setData: setItems } = useAsyncResource<JudicialNotification[]>(
    fetchItems,
    [],
    [creditId],
  );

  const create = async (payload: JudicialNotificationCreatePayload): Promise<JudicialNotification | null> => {
    setCreating(true);
    try {
      const created: JudicialNotification = await apiClient("/judicial-notifications", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setItems((prev) => [created, ...prev]);
      return created;
    } catch {
      return null;
    } finally {
      setCreating(false);
    }
  };

  const updateItem = (updated: JudicialNotification) => {
    setItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
  };

  return { items, loading, error, creating, refetch, create, updateItem };
};
