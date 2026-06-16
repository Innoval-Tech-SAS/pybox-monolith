import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  Campaign,
  CampaignCreatePayload,
  CampaignUpdatePayload,
} from "@/types/campaigns/campaign-types";

export const useCampaigns = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [items, setItems] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchItems = useCallback(() => {
    if (!organizationId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/campaigns/?organizationId=${organizationId}`, { method: "GET" })
      .then((data: Campaign[]) => setItems(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [organizationId, apiClient]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const create = async (payload: CampaignCreatePayload): Promise<Campaign | null> => {
    setSaving(true);
    try {
      const created: Campaign = await apiClient(
        `/campaigns/?organizationId=${organizationId}`,
        { method: "POST", body: JSON.stringify(payload) },
      );
      setItems((prev) => [created, ...prev]);
      return created;
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const update = async (id: string, payload: CampaignUpdatePayload): Promise<Campaign | null> => {
    setSaving(true);
    try {
      const updated: Campaign = await apiClient(
        `/campaigns/${id}?organizationId=${organizationId}`,
        { method: "PATCH", body: JSON.stringify(payload) },
      );
      setItems((prev) => prev.map((c) => (c.id === id ? updated : c)));
      return updated;
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: string): Promise<boolean> => {
    setSaving(true);
    try {
      await apiClient(`/campaigns/${id}?organizationId=${organizationId}`, { method: "DELETE" });
      setItems((prev) => prev.filter((c) => c.id !== id));
      return true;
    } catch {
      return false;
    } finally {
      setSaving(false);
    }
  };

  const activate = async (id: string): Promise<Campaign | null> => {
    setSaving(true);
    try {
      const updated: Campaign = await apiClient(
        `/campaigns/${id}/activate?organizationId=${organizationId}`,
        { method: "POST" },
      );
      setItems((prev) => prev.map((c) => (c.id === id ? updated : c)));
      return updated;
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const pause = async (id: string): Promise<Campaign | null> => {
    setSaving(true);
    try {
      const updated: Campaign = await apiClient(
        `/campaigns/${id}/pause?organizationId=${organizationId}`,
        { method: "POST" },
      );
      setItems((prev) => prev.map((c) => (c.id === id ? updated : c)));
      return updated;
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  return { items, loading, saving, refetch: fetchItems, create, update, remove, activate, pause };
};
