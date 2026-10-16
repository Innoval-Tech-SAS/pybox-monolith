import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DebtorSendingChannelGroup } from "@/types/companies/portfolio-debtor-types";

export const useDebtorSendingsHistory = (
  debtorId: string | null,
  portfolioId: string,
  page: number,
  pageSize = 20,
) => {
  const { apiClient } = useApiClient();
  const [groups, setGroups] = useState<DebtorSendingChannelGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(() => {
    if (!debtorId || !portfolioId) {
      setGroups([]);
      return;
    }
    setLoading(true);
    setError(null);
    apiClient<DebtorSendingChannelGroup[]>(`/contacts/debtor/${debtorId}?portfolioId=${portfolioId}&page=${page}&pageSize=${pageSize}`)
      .then((d) => setGroups(d ?? []))
      .catch((err) => setError(err instanceof Error ? err.message : "Error al cargar el historial de envíos"))
      .finally(() => setLoading(false));
  }, [debtorId, portfolioId, page, pageSize, apiClient]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return { groups, loading, error, refetch: fetchHistory };
};
