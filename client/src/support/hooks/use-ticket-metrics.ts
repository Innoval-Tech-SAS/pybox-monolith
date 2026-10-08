import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { TicketMetrics } from "@/types/support/support-types";

export const useTicketMetrics = () => {
  const { apiClient } = useApiClient();
  const { data: metrics, loading, refetch } = useAsyncResource<TicketMetrics | null>(
    () => apiClient("/cs/tickets/metrics"),
    null,
    [],
  );

  return { metrics, loading, refetch };
};
