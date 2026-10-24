import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { CampaignOccurrence, CampaignTimelineResponse } from "@/types/campaigns/campaign-types";

export const useCampaignTimeline = (
  organizationId: string,
  from: string,
  to: string,
) => {
  const { apiClient } = useApiClient();
  const [occurrences, setOccurrences] = useState<CampaignOccurrence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTimeline = useCallback(() => {
    if (!organizationId || !from || !to) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    const params = new URLSearchParams({ organizationId, from, to });
    apiClient(`/campaigns/timeline?${params}`, { method: "GET" })
      .then((data: CampaignTimelineResponse) => setOccurrences(data.items ?? []))
      .catch(() => {
        setOccurrences([]);
        setError("No se pudo cargar el calendario de campañas");
      })
      .finally(() => setLoading(false));
  }, [organizationId, from, to, apiClient]);

  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  return { occurrences, loading, error, refetch: fetchTimeline };
};
