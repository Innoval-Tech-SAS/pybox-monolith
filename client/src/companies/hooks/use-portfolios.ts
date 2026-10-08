import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { Portfolio } from "@/types/companies/portfolio-types";

export const usePortfolios = (orgId: string) => {
  const { apiClient } = useApiClient();

  const fetchPortfolios = useCallback(() => {
    if (!orgId) return Promise.resolve([]);
    return apiClient(`/portfolios/?organizationId=${orgId}`) as Promise<Portfolio[]>;
  }, [orgId, apiClient]);

  const { data: portfolios, loading, error, refetch } = useAsyncResource<Portfolio[]>(
    fetchPortfolios,
    [],
    [orgId],
  );

  return { portfolios, loading, error, refetch };
};
