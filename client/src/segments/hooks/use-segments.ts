import { useState, useEffect } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SegmentResponse } from "@/segments/types/segment.types";

export const useSegments = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [segments, setSegments] = useState<SegmentResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = () => {
    if (!orgId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/segments/?organizationId=${orgId}`)
      .then((data: SegmentResponse[]) => setSegments(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetch(); }, [orgId]);

  const deleteSegment = async (id: string) => {
    await apiClient(`/segments/${id}?organizationId=${orgId}`, { method: "DELETE" });
    setSegments((prev) => prev.filter((s) => s.id !== id));
  };

  return { segments, loading, refetch: fetch, deleteSegment };
};
