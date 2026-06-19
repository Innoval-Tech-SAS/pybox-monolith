import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SegmentListResponse, SegmentResponse } from "@/segments/types/segment.types";

const PAGE_SIZE = 20;

export const useSegments = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [segments, setSegments] = useState<SegmentResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const fetchPage = useCallback((p: number) => {
    if (!orgId) { setLoading(false); return; }
    setLoading(true);
    const params = new URLSearchParams({
      organizationId: orgId,
      page: String(p),
      pageSize: String(PAGE_SIZE),
    });
    apiClient(`/segments/?${params}`)
      .then((data: SegmentListResponse) => {
        setSegments(data.items ?? []);
        setTotal(data.total ?? 0);
      })
      .catch(() => {
        setSegments([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [orgId, apiClient]);

  useEffect(() => {
    setPage(1);
    fetchPage(1);
  }, [fetchPage]);

  const goToPage = (p: number) => {
    setPage(p);
    fetchPage(p);
  };

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const deleteSegment = async (id: string) => {
    await apiClient(`/segments/${id}?organizationId=${orgId}`, { method: "DELETE" });
    const targetPage = segments.length === 1 && page > 1 ? page - 1 : page;
    setPage(targetPage);
    fetchPage(targetPage);
  };

  return {
    segments, total, page, pages, loading,
    refetch: () => fetchPage(page), goToPage,
    deleteSegment,
  };
};
