import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  Campaign,
  CampaignCreatePayload,
  CampaignListResponse,
  CampaignUpdatePayload,
} from "@/types/campaigns/campaign-types";

export type CampaignSortKey = "name" | "status";

export const useCampaigns = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [items, setItems] = useState<Campaign[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState("");
  const [pageSize, setPageSize] = useState(20);
  const [sortKey, setSortKey] = useState<CampaignSortKey>("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const fetchPage = useCallback((p: number) => {
    if (!portfolioId) { setLoading(false); return; }
    setLoading(true);
    const params = new URLSearchParams({
      portfolioId,
      page: String(p),
      pageSize: String(pageSize),
    });
    if (search) params.set("search", search);
    params.set("sort", sortKey);
    params.set("sort_order", sortOrder);
    apiClient(`/campaigns/?${params}`, { method: "GET" })
      .then((data: CampaignListResponse) => {
        setItems(data.items ?? []);
        setTotal(data.total ?? 0);
      })
      .catch(() => {
        setItems([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [portfolioId, apiClient, search, pageSize, sortKey, sortOrder]);

  useEffect(() => {
    setPage(1);
    fetchPage(1);
  }, [fetchPage]);

  const goToPage = (p: number) => {
    setPage(p);
    fetchPage(p);
  };

  const handleSort = (key: CampaignSortKey) => {
    if (key === sortKey) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortOrder("asc");
    }
  };

  const pages = Math.max(1, Math.ceil(total / pageSize));

  const create = async (payload: CampaignCreatePayload): Promise<Campaign | null> => {
    setSaving(true);
    try {
      const created: Campaign = await apiClient(
        `/campaigns/?portfolioId=${portfolioId}`,
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

  const update = async (id: string, payload: CampaignUpdatePayload): Promise<Campaign | null> => {
    setSaving(true);
    try {
      const updated: Campaign = await apiClient(
        `/campaigns/${id}?portfolioId=${portfolioId}`,
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
      await apiClient(`/campaigns/${id}?portfolioId=${portfolioId}`, { method: "DELETE" });
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

  const activate = async (id: string): Promise<Campaign | null> => {
    setSaving(true);
    try {
      const updated: Campaign = await apiClient(
        `/campaigns/${id}/activate?portfolioId=${portfolioId}`,
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
        `/campaigns/${id}/pause?portfolioId=${portfolioId}`,
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

  return {
    items, total, page, pages, loading, saving,
    search, setSearch,
    pageSize, setPageSize,
    sortKey, sortOrder, handleSort,
    refetch: () => fetchPage(page), goToPage,
    create, update, remove, activate, pause,
  };
};
