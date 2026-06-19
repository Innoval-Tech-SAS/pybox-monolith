import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { SegmentResponse } from "@/segments/types/segment.types";

export const useSegmentOptions = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [segments, setSegments] = useState<SegmentResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orgId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/segments/options?organizationId=${orgId}`)
      .then((data: SegmentResponse[]) => setSegments(data ?? []))
      .catch(() => setSegments([]))
      .finally(() => setLoading(false));
  }, [orgId, apiClient]);

  return { segments, loading };
};
