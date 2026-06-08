import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  Template,
  TemplateCreatePayload,
  TemplatePreviewResponse,
  TemplateSendRequest,
  TemplateSendResponse,
  TemplateUpdatePayload,
} from "@/types/templates/template-types";

export const useTemplates = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [items, setItems] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchItems = useCallback(() => {
    if (!organizationId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/templates/?organizationId=${organizationId}`, { method: "GET" })
      .then((data: Template[]) => setItems(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [organizationId, apiClient]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const create = async (payload: TemplateCreatePayload): Promise<Template | null> => {
    setSaving(true);
    try {
      const created: Template = await apiClient(
        `/templates/?organizationId=${organizationId}`,
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

  const update = async (id: string, payload: TemplateUpdatePayload): Promise<Template | null> => {
    setSaving(true);
    try {
      const updated: Template = await apiClient(
        `/templates/${id}?organizationId=${organizationId}`,
        { method: "PATCH", body: JSON.stringify(payload) },
      );
      setItems((prev) => prev.map((t) => (t.id === id ? updated : t)));
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
      await apiClient(`/templates/${id}?organizationId=${organizationId}`, { method: "DELETE" });
      setItems((prev) => prev.filter((t) => t.id !== id));
      return true;
    } catch {
      return false;
    } finally {
      setSaving(false);
    }
  };

  const preview = async (
    id: string,
    sub: Record<string, string>,
  ): Promise<TemplatePreviewResponse | null> => {
    try {
      return await apiClient(
        `/templates/${id}/preview?organizationId=${organizationId}`,
        { method: "POST", body: JSON.stringify({ sub }) },
      );
    } catch {
      return null;
    }
  };

  const send = async (
    id: string,
    data: TemplateSendRequest,
  ): Promise<TemplateSendResponse | null> => {
    setSaving(true);
    try {
      return await apiClient(
        `/templates/${id}/send?organizationId=${organizationId}`,
        { method: "POST", body: JSON.stringify(data) },
      );
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  return { items, loading, saving, refetch: fetchItems, create, update, remove, preview, send };
};
