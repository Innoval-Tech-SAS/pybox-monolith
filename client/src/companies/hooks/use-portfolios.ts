import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { Portfolio } from "@/types/companies/portfolio-types";

export const usePortfolios = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = () => {
    if (!orgId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/portfolios/?organizationId=${orgId}`)
      .then((data: Portfolio[]) => setPortfolios(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetch(); }, [orgId]);

  return { portfolios, loading, refetch: fetch };
};
