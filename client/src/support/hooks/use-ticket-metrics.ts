import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { TicketMetrics } from "@/types/support/support-types";

export const useTicketMetrics = () => {
  const { apiClient } = useApiClient();
  const [metrics, setMetrics] = useState<TicketMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  const fetch = useCallback(() => {
    setLoading(true);
    apiClient("/cs/tickets/metrics")
      .then((data: TicketMetrics) => setMetrics(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [apiClient]);

  useEffect(() => { fetch(); }, [fetch]);

  return { metrics, loading, refetch: fetch };
};
