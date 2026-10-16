import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DebtorStatementListResponse } from "@/types/companies/portfolio-debtor-types";

export const useDebtorStatements = (debtorId: string | null, portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [data, setData] = useState<DebtorStatementListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatements = useCallback(() => {
    if (!debtorId || !portfolioId) {
      setData(null);
      return;
    }
    setLoading(true);
    setError(null);
    apiClient<DebtorStatementListResponse>(`/debtors/${debtorId}/statements?portfolioId=${portfolioId}`)
      .then((d) => setData(d))
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar los extractos"))
      .finally(() => setLoading(false));
  }, [debtorId, portfolioId, apiClient]);

  useEffect(() => {
    fetchStatements();
  }, [fetchStatements]);

  return { items: data?.items ?? [], total: data?.total ?? 0, loading, error, refetch: fetchStatements };
};
