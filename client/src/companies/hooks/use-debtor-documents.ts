import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DebtorDocumentListResponse } from "@/types/companies/portfolio-debtor-types";

export const useDebtorDocuments = (debtorId: string | null, portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [data, setData] = useState<DebtorDocumentListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(() => {
    if (!debtorId || !portfolioId) {
      setData(null);
      return;
    }
    setLoading(true);
    setError(null);
    apiClient<DebtorDocumentListResponse>(`/debtors/${debtorId}/documents?portfolioId=${portfolioId}`)
      .then((d) => setData(d))
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar los archivos"))
      .finally(() => setLoading(false));
  }, [debtorId, portfolioId, apiClient]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return { items: data?.items ?? [], total: data?.total ?? 0, loading, error, refetch: fetchDocuments };
};
