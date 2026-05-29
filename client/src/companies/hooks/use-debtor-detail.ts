import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DebtorCredit, RelatedContactsResponse } from "@/types/companies/portfolio-debtor-types";

export const useDebtorRelatedContacts = (debtorId: number | null, portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [data, setData] = useState<RelatedContactsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!debtorId || !portfolioId) {
      setData(null);
      return;
    }
    setLoading(true);
    apiClient(`/debtors/${debtorId}/related-contacts?portfolioId=${portfolioId}`)
      .then((d: RelatedContactsResponse) => setData(d))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [debtorId, portfolioId]);

  return { data, loading };
};

export const useDebtorCredits = (debtorId: number | null, portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [credits, setCredits] = useState<DebtorCredit[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!debtorId || !portfolioId) {
      setCredits([]);
      return;
    }
    setLoading(true);
    apiClient(`/debtors/${debtorId}/credits?portfolioId=${portfolioId}`)
      .then((d: DebtorCredit[]) => setCredits(d ?? []))
      .catch(() => setCredits([]))
      .finally(() => setLoading(false));
  }, [debtorId, portfolioId]);

  return { credits, loading };
};
