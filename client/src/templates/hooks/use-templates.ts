import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  Template,
  TemplateCreatePayload,
  TemplateListResponse,
  TemplatePreviewResponse,
  TemplateSendRequest,
  TemplateSendResponse,
  TemplateUpdatePayload,
} from "@/types/templates/template-types";

const PAGE_SIZE = 20;

export const useTemplates = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [items, setItems] = useState<Template[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchPage = useCallback((p: number) => {
    if (!organizationId) { setLoading(false); return; }
    setLoading(true);
    const params = new URLSearchParams({
      organizationId,
      page: String(p),
      pageSize: String(PAGE_SIZE),
    });
    apiClient(`/templates/?${params}`, { method: "GET" })
      .then((data: TemplateListResponse) => {
        setItems(data.items ?? []);
        setTotal(data.total ?? 0);
      })
      .catch(() => {
        setItems([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [organizationId, apiClient]);

  useEffect(() => {
    setPage(1);
    fetchPage(1);
  }, [fetchPage]);

  const goToPage = (p: number) => {
    setPage(p);
    fetchPage(p);
  };

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const create = async (payload: TemplateCreatePayload): Promise<Template | null> => {
    setSaving(true);
    try {
      const created: Template = await apiClient(
        `/templates/?organizationId=${organizationId}`,
        { method: "POST", body: JSON.stringify(payload) },
      );
      setPage(1);
      fetchPage(1);
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
      const targetPage = items.length === 1 && page > 1 ? page - 1 : page;
      setPage(targetPage);
      fetchPage(targetPage);
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

  return {
    items, total, page, pages, loading, saving,
    refetch: () => fetchPage(page), goToPage,
    create, update, remove, preview, send,
  };
};
