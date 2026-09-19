import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { EntityResponse } from "@/query-builder/types/query-builder-types";

export const useSegmentOptions = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [segments, setSegments] = useState<EntityResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!portfolioId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/segments/options?portfolioId=${portfolioId}`)
      .then((data: EntityResponse[]) => setSegments(data ?? []))
      .catch(() => setSegments([]))
      .finally(() => setLoading(false));
  }, [portfolioId, apiClient]);

  return { segments, loading };
};
