import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PortfolioAccessEntry } from "@/types/users/portfolio-access-types";

export const useUserPortfolioAccess = (orgId: string, userId: string) => {
  const { apiClient } = useApiClient();
  const [portfolios, setPortfolios] = useState<PortfolioAccessEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPortfolios = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiClient<PortfolioAccessEntry[]>(
        `/organizations/${orgId}/members/${userId}/portfolios`
      );
      setPortfolios(data);
    } catch {
      setPortfolios([]);
    } finally {
      setLoading(false);
    }
  }, [orgId, userId, apiClient]);

  useEffect(() => { fetchPortfolios(); }, [fetchPortfolios]);

  const grantAccess = async (portfolioId: string): Promise<boolean> => {
    try {
      await apiClient<unknown>(`/organizations/${orgId}/members/${userId}/portfolios/${portfolioId}`, {
        method: "PUT",
      });
      await fetchPortfolios();
      return true;
    } catch {
      return false;
    }
  };

  const revokeAccess = async (portfolioId: string): Promise<boolean> => {
    try {
      await apiClient<unknown>(`/organizations/${orgId}/members/${userId}/portfolios/${portfolioId}`, {
        method: "DELETE",
      });
      await fetchPortfolios();
      return true;
    } catch {
      return false;
    }
  };

  return { portfolios, loading, grantAccess, revokeAccess, refetch: fetchPortfolios };
};
